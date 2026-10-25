# B3-1 AWS VPC & EC2 웹 인프라 구축 및 검증 단계별 완벽 가이드 (STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE)

---

## 1. 개요

본 문서는 B3-1 과제의 인프라를 처음부터 끝까지 무결하게 프로비저닝하고, 외부 접속을 실증하며, 과금 없이 안전하게 완전 철거하기 위한 **실무 엔지니어링 5단계 실행 가이드**입니다.

```
[STEP 1] AWS CLI 환경 준비 및 최소권한 자격증명 구성
   │
   ▼
[STEP 2] 원클릭 스크립트를 통한 VPC 및 EC2 Nginx 자동 배포
   │
   ▼
[STEP 3] 로컬 및 외부 브라우저 200 OK E2E 접근 실증 및 증빙 획득
   │
   ▼
[STEP 4] 3대 장애 시나리오 모의 검증 (트러블슈팅 실증)
   │
   ▼
[STEP 5] 5대 리소스 완전 철거 및 과금 0원 검증
```

---

## 2. STEP 1: AWS CLI 환경 준비 및 자격증명 구성

### 1) AWS CLI 설치 확인
터미널에서 AWS CLI가 설치되어 있는지 확인합니다.
```bash
aws --version
```
- 만약 설치되어 있지 않다면:
  - macOS: `brew install awscli` 또는 공식 PKG 설치
  - Linux: `curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install`

### 2) 최소권한 IAM 자격증명 등록 (`aws configure`)
루트 계정 대신 본 과제 전용 IAM 사용자의 Access Key를 등록합니다.
```bash
aws configure
```
```text
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: ap-northeast-2
Default output format [None]: json
```
- **검증**:
  ```bash
  aws sts get-caller-identity
  ```
  출력된 `Arn`이 루트 계정이 아닌 IAM 사용자임을 확인합니다.

---

## 3. STEP 2: 인프라 자동 배포 스크립트 실행

프로젝트 디렉터리에서 제공된 배포 스크립트를 실행합니다.
```bash
cd /Users/hwangjeonghyeon/codyssey_2026/2-1/B3-1
./scripts/deploy_infra.sh
```

### 터미널 진행 상황 및 단계별 동작:
1. 관리자 공인 IP 자동 조회 (`checkip.amazonaws.com`)
2. VPC 생성 (`10.0.0.0/16`) 및 DNS 호스트네임 활성화
3. Public Subnet 생성 (`10.0.1.0/24`, `ap-northeast-2a`)
4. Internet Gateway 생성 및 VPC 결합
5. Route Table 생성 및 `0.0.0.0/0 -> IGW` 라우팅 등록 후 서브넷 결합
6. Security Group 생성: HTTP 80 전역(`0.0.0.0/0`) 및 SSH 22 관리자IP(`/32`) 등록
7. SSH 키페어 생성 (`~/.ssh/b3-1-keypair.pem`, `chmod 400`)
8. Ubuntu 22.04 LTS AMI 동적 조회 및 User Data(Nginx 자동설치) 인라인 작성
9. EC2 인스턴스 런치 (`t2.micro`, 퍼블릭 IP 자동 할당, `DeleteOnTermination: true`)
10. 인스턴스 Running 대기 및 E2E 헬스체크 폴링 수행

---

## 4. STEP 3: E2E 외부 접속 실증 및 증빙 획득

배포가 완료되면 터미널에 할당된 공인 IP(`PUBLIC_IP`)가 출력됩니다.

### 1) 외부 브라우저 접속 실증 (A)
- 웹 브라우저 주소창에 `http://<할당된_공인_IP>` 입력.
- **기대 결과**: "Codyssey B3-1 AWS Web Service" 글래스모피즘 웰컴 화면 정상 표시.
- **증빙**: 브라우저 주소창(공인 IP)과 웹 페이지 본문이 함께 보이도록 전체 화면 캡처 저장.

### 2) 인프라 헬스체크 엔드포인트 실증 (B)
- 터미널에서 다음 명령 실행:
  ```bash
  curl -i "http://<할당된_공인_IP>/health"
  ```
  ```http
  HTTP/1.1 200 OK
  Server: nginx
  Content-Type: text/plain
  Content-Length: 3

  OK
  ```
- **증빙**: 터미널 출력 화면 캡처.

### 3) SSH 원격 접속 및 인스턴스 내부 헬스체크 (C)
- 생성된 키페어로 SSH 접속:
  ```bash
  ssh -i ~/.ssh/b3-1-keypair.pem ubuntu@<할당된_공인_IP>
  ```
- 인스턴스 내부에서 로컬 헬스체크:
  ```bash
  curl -i http://localhost
  systemctl status nginx
  exit
  ```

---

## 5. STEP 4: 트러블슈팅 실증 시나리오 테스트

평가 및 학습을 위해 의도적으로 보안 그룹의 80번 포트를 닫아 장애를 유발하고 복구하는 실증을 진행합니다.

1. **장애 유발**: 보안 그룹에서 80번 포트 규칙 임시 제거:
   ```bash
   SG_ID=$(aws ec2 describe-security-groups --filters "Name=tag:Name,Values=B3-1-WebInfra-SG" --region ap-northeast-2 --query 'SecurityGroups[0].GroupId' --output text)
   aws ec2 revoke-security-group-ingress --group-id "${SG_ID}" --protocol tcp --port 80 --cidr 0.0.0.0/0 --region ap-northeast-2
   ```
2. **증상 관측**: `curl -i --connect-timeout 3 http://<공인IP>/` ➔ `Connection timed out` 에러 확인.
3. **복구 조치**: 80번 포트 재등록:
   ```bash
   aws ec2 authorize-security-group-ingress --group-id "${SG_ID}" --protocol tcp --port 80 --cidr 0.0.0.0/0 --region ap-northeast-2
   ```
4. **결과 확인**: `curl -i http://<공인IP>/health` ➔ `HTTP/1.1 200 OK` 즉시 복구 확인.

---

## 6. STEP 5: 자원 완전 철거 및 무과금(Zero-Billing) 검증

실습이 끝난 후 제공된 철거 스크립트를 1회 실행하여 모든 클라우드 자원을 0원으로 정리합니다.

```bash
./scripts/cleanup_infra.sh
```

### 철거 완료 후 AWS 콘솔 최종 확인 3대 체크리스트:
1. **EC2 콘솔**: 인스턴스 상태가 `Terminated`이며 `Volumes` 메뉴에 미사용 볼륨이 전혀 없는가?
2. **VPC 콘솔**: 생성했던 `B3-1-WebInfra-VPC`, 서브넷, 인터넷 게이트웨이가 완전히 사라졌는가?
3. **Billing 콘솔**: 결제 대시보드(Bills)에서 실행 중인 유휴 리소스가 0건인가?
