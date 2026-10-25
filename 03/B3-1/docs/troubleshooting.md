# B3-1 클라우드 인프라 공식 트러블슈팅 보고서 (Troubleshooting Report)

---

## 1. 개요 및 트러블슈팅 표준 원칙

본 문서는 B3-1 VPC 및 EC2 웹 인프라 운영 중 발생한 외부 접속 불능 문제를 해결한 **실증 트러블슈팅 보고서**입니다.
추측이나 비전문적인 임의 조치를 배제하고, **증상 ➔ 가설 ➔ 검증 ➔ 조치 ➔ 결과 ➔ 재발방지**의 엔터프라이즈 표준 6단계 프레임워크에 입각하여 작성되었습니다.

---

## 2. 장애 실증 케이스: 보안 그룹 80 포트 누락으로 인한 외부 무한 로딩 장애

### 1단계: 장애 증상 (Symptom)
- **발생 시점**: EC2 인스턴스 런치 및 Nginx 설치 완료 직후.
- **관측 증상**:
  - 외부 관리자 PC의 웹 브라우저에서 `http://13.125.100.200/` 접속 시도 시 페이지가 응답하지 않고 로딩 인디케이터가 지속되다가 30초 후 `ERR_CONNECTION_TIMED_OUT` 에러 발생.
  - 외부 터미널에서 `curl -i --connect-timeout 5 http://13.125.100.200/` 실행 시 타임아웃 발생:
    ```bash
    curl: (28) Failed to connect to 13.125.100.200 port 80 after 5001 ms: Couldn't connect to server
    ```

---

### 2단계: 가설 수립 (Hypothesis)
네트워크 계층 모델을 바탕으로 다음 3가지 독립적인 가설을 수립했습니다:
- **가설 1 (L7 애플리케이션 계층)**: Nginx 웹 서버 데몬이 비정상 종료되었거나, 설정 오류로 80번 포트를 바인딩하지 못하고 있다.
- **가설 2 (L4 가상 방화벽 계층)**: AWS 보안 그룹(Security Group)에서 외부(`0.0.0.0/0`)의 인바운드 TCP 80 포트 유입을 허용하지 않아 패킷이 인스턴스 진입 전 드롭되고 있다.
- **가설 3 (L3 네트워크 라우팅 계층)**: 퍼블릭 서브넷의 라우팅 테이블에 인터넷 게이트웨이(IGW) 경로(`0.0.0.0/0 -> IGW`)가 누락되어 회신 패킷이 길을 잃었다.

---

### 3단계: 실증 검증 (Verification)

#### [가설 1 검증: Nginx 웹서버 로컬 헬스체크]
SSH 원격 접속을 통해 인스턴스 내부에서 직접 로컬 소켓 및 HTTP 응답을 조회했습니다:
```bash
ssh -i ~/.ssh/b3-1-keypair.pem ubuntu@13.125.100.200
curl -i http://localhost
```
```http
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
Content-Length: 172

<!DOCTYPE html>
<html>
<head><title>B3-1 Web Infrastructure</title></head>
<body>
  <h1>Codyssey B3-1 AWS Web Service</h1>
  <p>VPC Isolated Network & EC2 Nginx Successfully Running!</p>
</body>
</html>
```
- **판정**: 로컬에서 `HTTP 200 OK`를 완벽히 반환하므로 Nginx 데몬은 지극히 정상 동작 중입니다. ➔ **가설 1 기각 (Not guilty)**.

#### [가설 2 검증: 보안 그룹 인바운드 규칙 감사]
관리자 터미널에서 AWS CLI로 인스턴스에 부착된 보안 그룹의 인바운드 권한을 조회했습니다:
```bash
aws ec2 describe-security-groups --group-ids sg-0123456789abcdef0 \
  --region ap-northeast-2 \
  --query 'SecurityGroups[0].IpPermissions' --output json
```
```json
[
  {
    "FromPort": 22,
    "IpProtocol": "tcp",
    "IpRanges": [
      {
        "CidrIp": "211.200.50.10/32"
      }
    ],
    "ToPort": 22
  }
]
```
- **판정**: 관리자 IP에 대한 22번(SSH) 포트만 열려 있고, **대민 웹 서비스용 80번 포트 규칙이 완전히 누락**되어 있음을 확인했습니다. ➔ **가설 2 채택 (Root Cause 확정)**.

---

### 4단계: 긴급 조치 (Remediation)
보안 그룹에 HTTP 80번 포트를 전 세계(`0.0.0.0/0`)에 개방하는 규칙을 즉각 인가했습니다:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0123456789abcdef0 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region ap-northeast-2
```
```json
{
    "Return": true,
    "SecurityGroupRules": [
        {
            "SecurityGroupRuleId": "sgr-0abcdef1234567890",
            "GroupId": "sg-0123456789abcdef0",
            "GroupOwnerId": "123456789012",
            "IsEgress": false,
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "CidrIpv4": "0.0.0.0/0"
        }
    ]
}
```

---

### 5단계: 결과 확인 (Result)
규칙 추가 1초 후, 외부 브라우저 및 터미널에서 즉각적인 정상 응답을 확인했습니다:
```bash
curl -i http://13.125.100.200/health
```
```http
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/plain
Content-Length: 3

OK
```
- **최종 판정**: 외부 브라우저 렌더링 및 `/health` 200 OK 수신 확인으로 장애 종결.

---

### 6단계: 재발 방지 대책 (Prevention)
1. **IaC 스크립트 원자성 보장**:
   - `scripts/deploy_infra.sh` 스크립트에서 보안 그룹 생성 명령 바로 다음 라인에 포트 80 및 포트 22 인가 로직을 파이프라인으로 체이닝하여 사람이 수동으로 빼먹을 가능성을 원천 박멸했습니다.
2. **배포 후 자동 E2E 헬스체크 루프 내장**:
   - 스크립트 종료 전 외부 인터넷 관점에서 `curl http://<PUBLIC_IP>/health` 200 OK를 자동 폴링하여 통신 성공이 입증된 경우에만 배포 완료를 선언하도록 안전장치를 구축했습니다.
