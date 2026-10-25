#!/usr/bin/env bash
# ==============================================================================
# Codyssey B3-1: AWS VPC 격리 네트워크 & EC2 Nginx 웹 인프라 원클릭 자동 배포 스크립트
# 서울 리전 (ap-northeast-2) 기준
# ==============================================================================
set -euo pipefail

# PATH에 사용자 로컬 bin 경로 추가
export PATH="/Users/hwangjeonghyeon/.local/bin:${PATH}"

# 1. 고정 상수 및 태그 선언
REGION="ap-northeast-2"
VPC_CIDR="10.0.0.0/16"
SUBNET_CIDR="10.0.1.0/24"
AZ="${REGION}a"
INSTANCE_TYPE="t2.micro"
KEY_NAME="b3-1-keypair"
TAG_PROJECT="B3-1-WebInfra"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/../app" && pwd)"

echo "========================================================================"
echo " [START] B3-1 AWS 인프라 자동 배포 파이프라인 가동"
echo " 리전: ${REGION} | VPC 대역: ${VPC_CIDR} | 서브넷: ${SUBNET_CIDR}"
echo "========================================================================"

# 2. 관리자 공인 IP 동적 조회 (22번 포트 화이트리스트용)
echo "[INFO] 관리자 공인 IP를 동적으로 조회합니다..."
MY_IP=$(curl -s --connect-timeout 5 https://checkip.amazonaws.com || curl -s --connect-timeout 5 https://api.ipify.org || echo "")

if [[ -z "${MY_IP}" ]]; then
  echo "[ERROR] 공인 IP를 조회할 수 없습니다. 인터넷 연결을 확인하십시오." >&2
  exit 1
fi
echo "[SUCCESS] 관리자 공인 IP: ${MY_IP}/32"

# 3. VPC 프로비저닝 및 DNS 속성 활성화
echo "[INFO] 1/7. VPC 생성 중 (${VPC_CIDR})..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block "${VPC_CIDR}" \
  --region "${REGION}" \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${TAG_PROJECT}-VPC},{Key=Project,Value=${TAG_PROJECT}}]" \
  --query 'Vpc.VpcId' --output text)
echo "[SUCCESS] VPC 생성 완료: ${VPC_ID}"

aws ec2 modify-vpc-attribute --vpc-id "${VPC_ID}" --enable-dns-hostnames "{\"Value\":true}" --region "${REGION}"
aws ec2 modify-vpc-attribute --vpc-id "${VPC_ID}" --enable-dns-support "{\"Value\":true}" --region "${REGION}"
echo "[SUCCESS] VPC DNS 호스트네임 활성화 완료"

# 4. 퍼블릭 서브넷 프로비저닝
echo "[INFO] 2/7. 퍼블릭 서브넷 생성 중 (${SUBNET_CIDR}, AZ: ${AZ})..."
SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id "${VPC_ID}" \
  --cidr-block "${SUBNET_CIDR}" \
  --availability-zone "${AZ}" \
  --region "${REGION}" \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${TAG_PROJECT}-Subnet},{Key=Project,Value=${TAG_PROJECT}}]" \
  --query 'Subnet.SubnetId' --output text)
echo "[SUCCESS] 서브넷 생성 완료: ${SUBNET_ID}"

# 5. 인터넷 게이트웨이(IGW) 생성 및 VPC 바인딩
echo "[INFO] 3/7. 인터넷 게이트웨이(IGW) 생성 및 VPC 바인딩 중..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --region "${REGION}" \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${TAG_PROJECT}-IGW},{Key=Project,Value=${TAG_PROJECT}}]" \
  --query 'InternetGateway.InternetGatewayId' --output text)

aws ec2 attach-internet-gateway --vpc-id "${VPC_ID}" --internet-gateway-id "${IGW_ID}" --region "${REGION}"
echo "[SUCCESS] IGW 생성 및 바인딩 완료: ${IGW_ID}"

# 6. 커스텀 라우팅 테이블 생성 및 디폴트 라우트 등록 (0.0.0.0/0 -> IGW)
echo "[INFO] 4/7. 커스텀 라우팅 테이블 생성 및 IGW 라우트 등록 중..."
RTB_ID=$(aws ec2 create-route-table \
  --vpc-id "${VPC_ID}" \
  --region "${REGION}" \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${TAG_PROJECT}-RTB},{Key=Project,Value=${TAG_PROJECT}}]" \
  --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route \
  --route-table-id "${RTB_ID}" \
  --destination-cidr-block "0.0.0.0/0" \
  --gateway-id "${IGW_ID}" \
  --region "${REGION}" >/dev/null

aws ec2 associate-route-table \
  --route-table-id "${RTB_ID}" \
  --subnet-id "${SUBNET_ID}" \
  --region "${REGION}" >/dev/null
echo "[SUCCESS] 라우팅 테이블 생성 및 서브넷 결합 완료: ${RTB_ID}"

# 7. 보안 그룹 생성 및 인바운드 화이트리스트 규칙 등록
echo "[INFO] 5/7. 보안 그룹 생성 및 접근 제어 규칙 설정 중..."
SG_ID=$(aws ec2 create-security-group \
  --group-name "${TAG_PROJECT}-SG" \
  --description "Security Group for B3-1 Web Infrastructure" \
  --vpc-id "${VPC_ID}" \
  --region "${REGION}" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${TAG_PROJECT}-SG},{Key=Project,Value=${TAG_PROJECT}}]" \
  --query 'GroupId' --output text)

# HTTP (80): 0.0.0.0/0 전역 허용
aws ec2 authorize-security-group-ingress \
  --group-id "${SG_ID}" \
  --protocol tcp --port 80 --cidr "0.0.0.0/0" \
  --region "${REGION}" >/dev/null

# SSH (22): 관리자 공인 IP 단일 허용 (0-65535 전면 개방 금지 준수)
aws ec2 authorize-security-group-ingress \
  --group-id "${SG_ID}" \
  --protocol tcp --port 22 --cidr "${MY_IP}/32" \
  --region "${REGION}" >/dev/null
echo "[SUCCESS] 보안 그룹 구성 완료: ${SG_ID} (HTTP 80 전역 / SSH 22 관리자한정)"

# 8. SSH 키페어 준비
echo "[INFO] 6/7. SSH 키페어 생성 중..."
mkdir -p "${HOME}/.ssh"
KEY_FILE="${HOME}/.ssh/${KEY_NAME}.pem"

# 기존 키가 있다면 삭제 후 재생성
aws ec2 delete-key-pair --key-name "${KEY_NAME}" --region "${REGION}" 2>/dev/null || true
rm -f "${KEY_FILE}"

aws ec2 create-key-pair \
  --key-name "${KEY_NAME}" \
  --region "${REGION}" \
  --query 'KeyMaterial' --output text > "${KEY_FILE}"

chmod 400 "${KEY_FILE}"
echo "[SUCCESS] 키페어 생성 및 권한 설정 완료: ${KEY_FILE} (chmod 400)"

# 9. 최신 Ubuntu 22.04 LTS AMI 조회
echo "[INFO] 7/7. 최신 공식 Ubuntu 22.04 LTS AMI 조회 중..."
AMI_ID=$(aws ec2 describe-images \
  --region "${REGION}" \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
            "Name=state,Values=available" \
  --query 'reverse(sort_by(Images, &CreationDate))[0].ImageId' --output text)
echo "[SUCCESS] 타깃 AMI 식별: ${AMI_ID}"

# User Data 스크립트 작성
INDEX_HTML_CONTENT=$(cat "${APP_DIR}/index.html")
USER_DATA=$(cat << EOF
#!/bin/bash
apt-get update -y
apt-get install -y nginx
systemctl start nginx
systemctl enable nginx

# 웰컴 페이지 배포
cat << 'HTML' > /var/www/html/index.html
${INDEX_HTML_CONTENT}
HTML

# 헬스체크 엔드포인트 배포
mkdir -p /var/www/html/health
echo "OK" > /var/www/html/health/index.html
EOF
)

# 10. EC2 인스턴스 프로비저닝 (퍼블릭 IP 자동 할당, DeleteOnTermination 강제)
echo "[INFO] EC2 인스턴스 런치 중 (${INSTANCE_TYPE})..."
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "${AMI_ID}" \
  --instance-type "${INSTANCE_TYPE}" \
  --key-name "${KEY_NAME}" \
  --security-group-ids "${SG_ID}" \
  --subnet-id "${SUBNET_ID}" \
  --associate-public-ip-address \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":8,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
  --user-data "${USER_DATA}" \
  --region "${REGION}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${TAG_PROJECT}-Instance},{Key=Project,Value=${TAG_PROJECT}}]" \
  --query 'Instances[0].InstanceId' --output text)
echo "[SUCCESS] 인스턴스 런치 완료: ${INSTANCE_ID}"

# 11. 인스턴스 러닝 대기 및 공인 IP 추출
echo "[INFO] 인스턴스가 러닝(running) 상태로 전환될 때까지 대기합니다..."
aws ec2 wait instance-running --instance-ids "${INSTANCE_ID}" --region "${REGION}"

PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "========================================================================"
echo " [배포 완료] AWS 인프라가 성공적으로 프로비저닝되었습니다!"
echo " 인스턴스 ID : ${INSTANCE_ID}"
echo " 할당된 공인 IP: ${PUBLIC_IP}"
echo " 접속 URL    : http://${PUBLIC_IP}"
echo " 헬스체크 URL : http://${PUBLIC_IP}/health"
echo " SSH 접속 명령 : ssh -i ${KEY_FILE} ubuntu@${PUBLIC_IP}"
echo "========================================================================"

# 12. 외부 접속 헬스체크 E2E 폴링 검증 (P-25 실증 게이트)
echo "[INFO] 외부 인터넷 관점에서 E2E 헬스체크를 수행합니다 (최대 60초 폴링)..."
SUCCESS=0
for i in {1..30}; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://${PUBLIC_IP}/health" || true)
  if [[ "${HTTP_STATUS}" == "200" ]]; then
    echo "[VERIFIED] E2E 헬스체크 검증 성공! (HTTP 200 OK 수신 확인)"
    SUCCESS=1
    break
  fi
  echo " 대기 중... (${i}/30회, 현재 상태: ${HTTP_STATUS})"
  sleep 2
done

if [[ ${SUCCESS} -eq 1 ]]; then
  echo " [CONGRATULATIONS] B3-1 과제의 모든 네트워크/컴퓨트 요구사항이 완벽하게 입증되었습니다."
else
  echo " [WARNING] 60초 내에 헬스체크 응답을 받지 못했습니다. User Data 설치 완료 여부를 확인하십시오."
fi
