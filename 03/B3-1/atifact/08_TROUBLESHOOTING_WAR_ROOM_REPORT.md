# B3-1 클라우드 인프라 트러블슈팅 워룸 보고서 (TROUBLESHOOTING_WAR_ROOM_REPORT)

---

## 1. 개요 및 엔지니어링 표준 프레임워크

실제 클라우드 환경에서는 "서버를 띄웠는데 외부에서 안 들어와요"라는 문의가 장애의 80% 이상을 차지합니다.
숙련된 엔지니어는 지레짐작으로 설정을 이것저것 바꾸지 않고, **증상 ➔ 가설 ➔ 검증 ➔ 조치 ➔ 결과 ➔ 재발방지**의 6단계 인과적 프레임워크에 따라 체계적으로 문제를 규명합니다.
본 문서는 B3-1 환경에서 발생할 수 있는 3대 대표 장애 시나리오를 워룸(War-Room) 형식으로 완벽하게 재구성하여 기술합니다.

---

## 2. 6단계 표준 트러블슈팅 프레임워크 정의

```
[1. 증상 기록] : 에러 메시지, HTTP 응답 코드, 접속 타임아웃 등 관측된 팩트 수집
       │
       ▼
[2. 가설 수립] : 네트워크 계층(L3, L4, L7) 및 클라우드 설정 기반 원인 가설 도출
       │
       ▼
[3. 실증 검증] : curl, ping, telnet, AWS CLI 등을 통한 가설의 참/거짓 판정
       │
       ▼
[4. 긴급 조치] : 보안 원칙을 훼손하지 않는 최소한의 정확한 구성 변경 적용
       │
       ▼
[5. 사후 확인] : 외부 클라이언트 관점에서의 E2E 정상 통신 재검증
       │
       ▼
[6. 재발 방지] : IaC 코드 반영 및 자동화 검증 룰 추가로 인적 실수 영구 배제
```

---

## 3. 3대 핵심 장애 시나리오 워룸 실증 보고서

### [시나리오 1] 보안 그룹 인바운드 80 포트 누락 장애 (가장 빈번한 장애)

#### 1. 증상 (Symptom)
- 외부 브라우저에서 `http://13.125.100.200/` 접속 시 브라우저 탭이 계속 돌다가 `ERR_CONNECTION_TIMED_OUT` 에러 발생.
- 로컬 맥 터미널에서 `curl -i --connect-timeout 5 http://13.125.100.200/` 실행 시 5초 후 타임아웃 종료.

#### 2. 가설 (Hypothesis)
- **가설 A**: Nginx 웹 서버 데몬이 죽어 있거나 80번 포트를 리스닝하지 않고 있다.
- **가설 B**: 보안 그룹(Security Group)에서 외부(0.0.0.0/0)의 TCP 80번 포트 유입을 차단하고 있다.
- **가설 C**: 인스턴스 내부 OS 방화벽(`ufw` 또는 `iptables`)이 트래픽을 거부하고 있다.

#### 3. 검증 (Verification)
- **가설 A 검증**: SSH로 EC2에 접속하여 내부 로컬 호출 수행:
  ```bash
  ssh -i ~/.ssh/b3-1-keypair.pem ubuntu@13.125.100.200
  curl -i http://localhost
  ```
  ```http
  HTTP/1.1 200 OK
  Server: nginx
  ...
  <h1>Codyssey B3-1 AWS Web Service</h1>
  ```
  ➔ 로컬 200 OK 반환. Nginx 프로세스는 정상 작동 중이므로 **가설 A 기각**.
- **가설 B 검증**: 관리자 PC에서 AWS CLI로 현재 보안 그룹 인바운드 규칙 조회:
  ```bash
  aws ec2 describe-security-groups --group-ids sg-0123456789abcdef0 \
    --query 'SecurityGroups[0].IpPermissions' --output json
  ```
  ```json
  [
    {
      "FromPort": 22,
      "IpProtocol": "tcp",
      "IpRanges": [{"CidrIp": "211.200.50.10/32"}],
      "ToPort": 22
    }
  ]
  ```
  ➔ 22번 포트만 열려 있고, 80번 포트 규칙이 누락되어 있음. **가설 B 채택(원인 확정)**.

#### 4. 조치 (Remediation)
- 보안 그룹에 HTTP 80번 포트 전역 개방 인바운드 규칙 즉각 추가:
  ```bash
  aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp --port 80 --cidr 0.0.0.0/0 \
    --region ap-northeast-2
  ```

#### 5. 결과 (Result)
- 외부 터미널에서 즉각 `HTTP/1.1 200 OK` 확인 및 브라우저 정상 렌더링 완료.
  ```bash
  curl -i http://13.125.100.200/health
  ```
  ```http
  HTTP/1.1 200 OK
  OK
  ```

#### 6. 재발방지 (Prevention)
- 인프라 배포 스크립트(`deploy_infra.sh`) 내에 보안 그룹 생성 후 즉시 80번 포트를 추가하는 로직을 자동화하여 수동 작업 누락 방지.

---

### [시나리오 2] 서브넷 라우팅 테이블(0.0.0.0/0 -> IGW) 누락 장애

#### 1. 증상 (Symptom)
- EC2 인스턴스에 공인 IP가 할당되어 있고 보안 그룹 80번이 열려 있음에도 외부 접속이 일체 불가능하고, EC2 내부에서 `curl https://example.com` 아웃바운드 호출 시에도 타임아웃 발생.

#### 2. 가설 (Hypothesis)
- **가설 A**: 인터넷 게이트웨이(IGW)가 VPC에 결합(Attach)되어 있지 않다.
- **가설 B**: 서브넷에 연결된 라우팅 테이블에 디폴트 라우트(`0.0.0.0/0 -> IGW`)가 누락되어 패킷이 나갈 경로를 찾지 못한다.

#### 3. 검증 (Verification)
- IGW 결합 상태 확인:
  ```bash
  aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=vpc-0a1b2c3d4e5f67890"
  ```
  ➔ `Attachments[0].State`가 `available`로 정상 결합됨 확인. (가설 A 기각)
- 서브넷 결합 라우팅 테이블 경로 확인:
  ```bash
  aws ec2 describe-route-tables --filters "Name=association.subnet-id,Values=subnet-0123456789abcdef0" \
    --query 'RouteTables[*].Routes' --output json
  ```
  ```json
  [
    [
      {
        "DestinationCidrBlock": "10.0.0.0/16",
        "GatewayId": "local",
        "State": "active"
      }
    ]
  ]
  ```
  ➔ 내부 `10.0.0.0/16` 로컬 경로만 존재하고 외부 인터넷 경로(`0.0.0.0/0`)가 전혀 없음! **가설 B 채택**.

#### 4. 조치 (Remediation)
- 라우팅 테이블에 디폴트 라우트 등록:
  ```bash
  aws ec2 create-route \
    --route-table-id rtb-0123456789abcdef0 \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id igw-0123456789abcdef0 \
    --region ap-northeast-2
  ```

#### 5. 결과 (Result)
- EC2 내부에서 아웃바운드 패키지 업데이트(`apt-get update`) 정상 통신 확인 및 외부 브라우저 접속 즉시 성공.

#### 6. 재발방지 (Prevention)
- 서브넷을 생성하면 반드시 전용 라우팅 테이블을 만들고 `create-route`를 원자적(Atomic)으로 묶어서 실행하도록 스크립트 파이프라인 구성.

---

### [시나리오 3] 퍼블릭 IP 자동 할당 비활성화 장애

#### 1. 증상 (Symptom)
- 인스턴스는 정상 기동(`running`)되었으나, AWS 콘솔이나 CLI에서 `PublicIpAddress` 필드가 비어 있고 외부에서 접속할 IP 주소 자체가 존재하지 않음.

#### 2. 가설 (Hypothesis)
- 인스턴스 런치 시 `--associate-public-ip-address` 플래그를 누락했거나, 서브넷의 `MapPublicIpOnLaunch` 속성이 false로 설정되어 있다.

#### 3. 검증 및 조치 (Verification & Remediation)
- 서브넷 속성 확인 및 인스턴스 런치 명령어 파라미터 점검:
  ```bash
  aws ec2 describe-instances --instance-ids i-0123456789abcdef0 \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
  # 출력: None
  ```
- **조치**: 탄력적 IP(EIP)를 임시로 발급하여 붙이거나, 스크립트의 `run-instances` 호출 시 반드시 `--associate-public-ip-address`를 명시적으로 전달하도록 수정.

---

## 4. 장애 대응 엔지니어 체크 시퀀스 다이어그램

```
[외부 접속 불능 장애 접수]
          │
          ▼
[1단계: 인스턴스 내부 검사] ──(curl localhost)──> [실패] ──> Nginx 데몬 / 설정 문법 에러 조치
          │ (성공)
          ▼
[2단계: 보안 그룹 검사]    ──(인바운드 80 확인)─> [누락] ──> SG 인바운드 80 (0.0.0.0/0) 추가
          │ (정상)
          ▼
[3단계: 라우팅 테이블 검사] ──(0.0.0.0/0 -> IGW)─> [누락] ──> create-route로 IGW 바인딩
          │ (정상)
          ▼
[4단계: 공인 IP 유무 검사]  ──(Public IPv4 존재)─> [누락] ──> 퍼블릭 IP 할당 및 재부팅
          │ (정상)
          ▼
[최종 E2E 검증 성공 (200 OK)]
```
