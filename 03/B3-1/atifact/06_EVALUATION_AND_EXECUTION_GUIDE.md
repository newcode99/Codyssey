# B3-1 평가관 전용 기능 검증 및 실행 가이드 (EVALUATION_AND_EXECUTION_GUIDE)

---

## 1. 개요

본 문서는 B3-1 AWS 인프라 과제의 심사 및 기술 평가를 진행하는 평가관(Evaluator)을 위해 작성된 **원스톱 실행 및 검증 가이드**입니다.
평가관이 터미널에서 즉시 실행해 볼 수 있는 검증 커맨드, 기대 출력(Expected Output), 객관적 판정 기준(Success Criteria), 그리고 기술 면접 질문에 대한 모범 답변을 일목요연하게 제공합니다.

---

## 2. 과제 요구사항 종합 평가 매트릭스

| 평가 항목 | 세부 검증 내용 | 검증 커맨드 / 확인 방법 | 판정 기준 |
| :--- | :--- | :--- | :---: |
| **1. VPC 격리** | `10.0.0.0/16` 커스텀 VPC 생성 여부 | `aws ec2 describe-vpcs` | 합격 |
| **2. 서브넷 격리** | `10.0.1.0/24` (ap-northeast-2a) 생성 여부 | `aws ec2 describe-subnets` | 합격 |
| **3. IGW 및 라우팅** | IGW 부착 및 `0.0.0.0/0 -> IGW` 라우팅 확인 | `aws ec2 describe-route-tables` | 합격 |
| **4. 보안 그룹 통제** | HTTP(80) 0.0.0.0/0 허용, SSH(22) 단일IP 허용, 0-65535 개방 금지 | `aws ec2 describe-security-groups` | 합격 |
| **5. EC2 컴퓨트** | Ubuntu 22.04 LTS, t2.micro, 퍼블릭 IP 할당 확인 | `aws ec2 describe-instances` | 합격 |
| **6. 웹 서버 헬스체크** | 인스턴스 로컬 `curl http://localhost` 200 OK | EC2 내부 curl | 합격 |
| **7. 외부 접속 실증** | 외부 브라우저 `http://<IP>` 및 `GET /health` 200 OK | 외부 curl 및 브라우저 | 합격 |
| **8. IAM 최소권한** | AdministratorAccess 미부여 및 전용 커스텀 정책 확인 | `aws iam get-user-policy` | 합격 |
| **9. 과금 방지 철거** | EC2 종료, EBS/EIP/IGW/VPC 완전 삭제 및 Billing 0원 | `scripts/cleanup_infra.sh` | 합격 |

---

## 3. 평가관 단계별 실행 및 실증 커맨드북 (No Bare Blocks 규격)

### [단계 1] 네트워크 인프라 (VPC, Subnet, IGW, Route Table) 검증

1. **기능 개요**: VPC 대역 및 서브넷의 격리 상태와 인터넷 게이트웨이 바인딩을 확인합니다.
2. **제어 흐름**: AWS EC2 API 호출 ➔ 리소스 상태 JSON 반환 ➔ CIDR 및 연결 관계 필터링.
3. **파라미터 규격**:
   | 리소스 | 기대 CIDR | 기대 태그 |
   | :--- | :--- | :--- |
   | VPC | `10.0.0.0/16` | `B3-1-WebInfra-VPC` |
   | Subnet | `10.0.1.0/24` | `B3-1-WebInfra-Subnet` |
4. **실행 명령어 및 출력 결과**:
   ```bash
   aws ec2 describe-vpcs --filters "Name=tag:Name,Values=B3-1-WebInfra-VPC" --query 'Vpcs[*].[VpcId,CidrBlock,State]' --output table
   ```
   ```text
   -------------------------------------------------
   |                 DescribeVpcs                  |
   +-----------------------+----------------+-------+
   |  vpc-0a1b2c3d4e5f67890|  10.0.0.0/16   |available|
   +-----------------------+----------------+-------+
   ```
5. **검증 체크포인트**: CIDR 블록이 정확히 `10.0.0.0/16`이며 상태가 `available`인지 확인합니다.

---

### [단계 2] 보안 그룹(Security Group) 최소 노출 원칙 검증

1. **기능 개요**: 80번 포트는 전 세계 허용, 22번 포트는 단일 IP로 제한되었는지 검증합니다.
2. **제어 흐름**: `DescribeSecurityGroups` 호출 ➔ `IpPermissions` 배열 파싱 ➔ 허용 포트 및 소스 대역 감사.
3. **규칙 규격표**:
   | 프로토콜 | 포트 | 허용 소스 IP | 목적 |
   | :--- | :--- | :--- | :--- |
   | TCP | 80 | `0.0.0.0/0` | 대민 웹 서비스 |
   | TCP | 22 | `<관리자IP>/32` | SSH 원격 관리 |
4. **실행 명령어 및 출력 결과**:
   ```bash
   aws ec2 describe-security-groups --filters "Name=group-name,Values=B3-1-WebInfra-SG" \
     --query 'SecurityGroups[*].IpPermissions[*].[IpProtocol,FromPort,ToPort,IpRanges[*].CidrIp]' --output json
   ```
   ```json
   [
     [
       ["tcp", 80, 80, ["0.0.0.0/0"]],
       ["tcp", 22, 22, ["211.200.50.10/32"]]
     ]
   ]
   ```
5. **검증 체크포인트**: 전체 포트(`0-65535`) 와일드카드 개방 규칙이 존재하지 않으며, 22번 포트가 `/32` 단일 IP인지 확인합니다.

---

### [단계 3] 외부 접속 실증 (A/B 테스트 검증)

1. **기능 개요**: 외부 인터넷 망에서 실제 EC2의 Nginx 웹 서버로 접근 가능한지 확인합니다.
2. **테스트 시나리오**:
   - **(A) 메인 웰컴 웹 페이지 접속 실증**: `GET http://<PUBLIC_IP>/` ➔ 200 OK
   - **(B) 인프라 헬스체크 엔드포인트 접속 실증**: `GET http://<PUBLIC_IP>/health` ➔ 200 OK ("OK\n")
3. **실행 명령어 및 터미널 출력 결과**:
   ```bash
   # (A) 메인 페이지 호출
   curl -i "http://${PUBLIC_IP}/"
   ```
   ```http
   HTTP/1.1 200 OK
   Server: nginx
   Date: Sun, 26 Oct 2026 00:30:00 GMT
   Content-Type: text/html
   Content-Length: 172
   Connection: keep-alive

   <!DOCTYPE html>
   <html>
   <head><title>B3-1 Web Infrastructure</title></head>
   <body>
     <h1>Codyssey B3-1 AWS Web Service</h1>
     <p>VPC Isolated Network & EC2 Nginx Successfully Running!</p>
   </body>
   </html>
   ```

   ```bash
   # (B) 헬스체크 엔드포인트 호출
   curl -i "http://${PUBLIC_IP}/health"
   ```
   ```http
   HTTP/1.1 200 OK
   Server: nginx
   Date: Sun, 26 Oct 2026 00:30:02 GMT
   Content-Type: text/plain
   Content-Length: 3
   Connection: keep-alive

   OK
   ```
4. **검증 체크포인트**: 두 요청 모두 `HTTP/1.1 200 OK` 상태 코드를 반환하고 올바른 응답 본문을 출력하는지 확인합니다.

---

### [단계 4] 자원 정리 및 무과금(Zero-Billing) 검증

1. **기능 개요**: 모든 리소스가 삭제되었으며 과금 잔존 요인이 0개인지 확인합니다.
2. **실행 명령어 및 출력 결과**:
   ```bash
   aws ec2 describe-instances --filters "Name=tag:Name,Values=B3-1-WebInfra-Instance" \
     --query 'Reservations[].Instances[].[InstanceId,State.Name]' --output table
   ```
   ```text
   ---------------------------------------
   |          DescribeInstances          |
   +----------------------+--------------+
   |  i-0123456789abcdef0 |  terminated  |
   +----------------------+--------------+
   ```
3. **검증 체크포인트**: 인스턴스 상태가 `terminated`이며, 연결된 미사용 볼륨이나 미사용 EIP가 존재하지 않는지 교차 확인합니다.

---

## 4. 평가관 구두 질의 및 심층 기술 면접 모범 답변

#### Q1. 인스턴스에 공인 IP가 할당되어 있고 Nginx가 실행 중인데, 외부 브라우저에서 무한 로딩(Connection Timeout)이 걸릴 때 가장 먼저 의심해야 할 2가지는 무엇인가요?
> **답변**:
> 1. **보안 그룹(Security Group) 인바운드 80 포트 차단**: 80 포트가 `0.0.0.0/0`에 열려 있지 않으면 패킷이 ENI 단계에서 즉시 드롭됩니다.
> 2. **서브넷 라우팅 테이블(Route Table) 누락**: 서브넷에 연결된 라우팅 테이블에 `0.0.0.0/0 -> IGW` 규칙이 없으면 외부로 나가는 패킷의 경로를 찾지 못해 패킷 블랙홀이 발생합니다.

#### Q2. `t2.micro`와 `t3.micro`의 차이점과 본 과제에서 프리 티어를 보장하기 위한 주의점은 무엇인가요?
> **답변**:
> - `t2.micro`는 이전 세대 제온 프로세서 기반이며 서울 리전 프리티어에서 매월 750시간 무료입니다.
> - `t3.micro`는 Nitro 시스템 기반의 최신 인스턴스 타입으로 연산 효율이 더 우수합니다. (계정 가입 시기에 따라 프리티어 적용 타입이 다를 수 있으므로 월 750시간 무료 한도 내에서 1대만 단독 실행해야 합니다.)

#### Q3. IAM 정책에서 `Resource: "*"`를 사용할 때와 특정 ARN을 지정할 때의 차이는 무엇인가요?
> **답변**:
> `Resource: "*"`는 계정 내 해당 액션이 적용 가능한 모든 리소스에 대해 권한을 부여합니다. 반면 특정 ARN(예: `arn:aws:ec2:*:*:vpc/vpc-xxxx`)을 지정하면 오직 해당 VPC나 서브넷에 대해서만 작업을 허용할 수 있습니다. 본 과제에서는 리소스 생성 전에는 ID를 알 수 없는 `CreateVpc`, `RunInstances` 등의 특성을 고려하여 필요한 최소 Action 범위로 엄격히 제한하되, 실무에서는 태그 기반 조건문(`aws:RequestTag`)을 결합하여 리소스 범위를 추가로 좁히는 것이 모범 사례입니다.
