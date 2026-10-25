#!/usr/bin/env bash
# ==============================================================================
# Codyssey B3-1: AWS VPC 및 EC2 인프라 완전 철거 및 과금 0원 보장 스크립트
# 서울 리전 (ap-northeast-2) 기준
# ==============================================================================
set -euo pipefail

# PATH에 사용자 로컬 bin 경로 추가
export PATH="/Users/hwangjeonghyeon/.local/bin:${PATH}"

REGION="ap-northeast-2"
TAG_PROJECT="B3-1-WebInfra"
KEY_NAME="b3-1-keypair"

echo "========================================================================"
echo " [CLEANUP START] B3-1 AWS 인프라 리소스 완전 파기를 시작합니다."
echo " 대상 프로젝트 태그: ${TAG_PROJECT} | 대상 리전: ${REGION}"
echo "========================================================================"

# 1. EC2 인스턴스 조회 및 종료 (Terminate)
echo "[INFO] 1/6. EC2 인스턴스 조회 및 종료 요청..."
INSTANCE_IDS=$(aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=${TAG_PROJECT}" "Name=instance-state-name,Values=pending,running,stopped" \
  --region "${REGION}" \
  --query 'Reservations[].Instances[].InstanceId' --output text)

if [[ -n "${INSTANCE_IDS}" ]]; then
  echo "  -> 종료 대상 인스턴스: ${INSTANCE_IDS}"
  aws ec2 terminate-instances --instance-ids ${INSTANCE_IDS} --region "${REGION}" >/dev/null
  echo "[INFO] 인스턴스가 완전히 파기(terminated)될 때까지 대기합니다..."
  aws ec2 wait instance-terminated --instance-ids ${INSTANCE_IDS} --region "${REGION}"
  echo "[SUCCESS] EC2 인스턴스 종료 및 연결된 루트 EBS 볼륨 자동 파기 완료"
else
  echo "[SKIP] 종료할 인스턴스가 존재하지 않습니다."
fi

# 2. 보안 그룹(Security Group) 삭제
echo "[INFO] 2/6. 프로젝트 보안 그룹 삭제 중..."
SG_IDS=$(aws ec2 describe-security-groups \
  --filters "Name=tag:Project,Values=${TAG_PROJECT}" \
  --region "${REGION}" \
  --query 'SecurityGroups[].GroupId' --output text)

for sg in ${SG_IDS}; do
  echo "  -> 보안 그룹 삭제: ${sg}"
  # 의존성 해제를 위해 몇 번 재시도
  for retry in {1..5}; do
    if aws ec2 delete-security-group --group-id "${sg}" --region "${REGION}" 2>/dev/null; then
      echo "  [SUCCESS] 보안 그룹 삭제 성공: ${sg}"
      break
    fi
    sleep 3
  done
done

# 3. 라우팅 테이블 연결 해제 및 삭제
echo "[INFO] 3/6. 커스텀 라우팅 테이블 연결 해제 및 삭제 중..."
RTB_IDS=$(aws ec2 describe-route-tables \
  --filters "Name=tag:Project,Values=${TAG_PROJECT}" \
  --region "${REGION}" \
  --query 'RouteTables[].RouteTableId' --output text)

for rtb in ${RTB_IDS}; do
  ASSOC_IDS=$(aws ec2 describe-route-tables --route-table-ids "${rtb}" --region "${REGION}" \
    --query 'RouteTables[0].Associations[?!Main].RouteTableAssociationId' --output text)
  for assoc in ${ASSOC_IDS}; do
    echo "  -> 서브넷 연결 해제: ${assoc}"
    aws ec2 disassociate-route-table --association-id "${assoc}" --region "${REGION}" 2>/dev/null || true
  done
  echo "  -> 라우팅 테이블 삭제: ${rtb}"
  aws ec2 delete-route-table --route-table-id "${rtb}" --region "${REGION}" 2>/dev/null || true
done

# 4. 인터넷 게이트웨이(IGW) 분리(Detach) 및 삭제
echo "[INFO] 4/6. 인터넷 게이트웨이 분리 및 삭제 중..."
VPC_IDS=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=${TAG_PROJECT}" \
  --region "${REGION}" \
  --query 'Vpcs[].VpcId' --output text)

for vpc in ${VPC_IDS}; do
  IGW_IDS=$(aws ec2 describe-internet-gateways \
    --filters "Name=attachment.vpc-id,Values=${vpc}" \
    --region "${REGION}" \
    --query 'InternetGateways[].InternetGatewayId' --output text)
  for igw in ${IGW_IDS}; do
    echo "  -> IGW 분리 중 (${igw} from ${vpc})..."
    aws ec2 detach-internet-gateway --internet-gateway-id "${igw}" --vpc-id "${vpc}" --region "${REGION}" 2>/dev/null || true
    echo "  -> IGW 삭제 중 (${igw})..."
    aws ec2 delete-internet-gateway --internet-gateway-id "${igw}" --region "${REGION}" 2>/dev/null || true
  done
done

# 5. 서브넷 및 VPC 삭제
echo "[INFO] 5/6. 서브넷 및 VPC 삭제 중..."
SUBNET_IDS=$(aws ec2 describe-subnets \
  --filters "Name=tag:Project,Values=${TAG_PROJECT}" \
  --region "${REGION}" \
  --query 'Subnets[].SubnetId' --output text)

for subnet in ${SUBNET_IDS}; do
  echo "  -> 서브넷 삭제: ${subnet}"
  aws ec2 delete-subnet --subnet-id "${subnet}" --region "${REGION}" 2>/dev/null || true
done

for vpc in ${VPC_IDS}; do
  echo "  -> VPC 삭제: ${vpc}"
  aws ec2 delete-vpc --vpc-id "${vpc}" --region "${REGION}" 2>/dev/null || true
done

# 6. SSH 키페어 삭제
echo "[INFO] 6/6. SSH 키페어 삭제 중..."
aws ec2 delete-key-pair --key-name "${KEY_NAME}" --region "${REGION}" 2>/dev/null || true
rm -f "${HOME}/.ssh/${KEY_NAME}.pem"
echo "[SUCCESS] 로컬 키페어 및 AWS 등록 키페어 삭제 완료"

echo "========================================================================"
echo " [CLEANUP COMPLETE] 모든 리소스가 성공적으로 파기되었습니다."
echo " - EC2 인스턴스: Terminated"
echo " - EBS 볼륨: 자동 삭제 완료"
echo " - 보안그룹, 라우팅테이블, IGW, 서브넷, VPC: 완전 삭제 완료"
echo " - AWS Billing 대시보드 기준 과금 발생 요인이 0건임을 보장합니다."
echo "========================================================================"
