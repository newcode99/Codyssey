# B3-1 AWS VPC 격리 네트워크 & EC2 웹 서비스 배포 과제 명세서 (TASK_SPECIFICATION)

---

## 1. 미션 개요 및 설계 의도

### 목적
"일단 서버에 올렸는데 외부에서 안 들어와요." 포트를 막아놓았거나, 보안 그룹이 없거나, 라우팅 테이블이 누락된 것입니다.
클라우드는 단순히 빠른 컴퓨터를 빌리는 것이 아니라 **네트워크(VPC/Subnet), 라우팅(IGW/Route Table), 경계 보안(Security Group), 접근 통제(IAM)** 가 유기적으로 결합된 격리된 인프라 환경입니다. 열린 포트 하나로 서버가 침해당할 수 있는 클라우드 환경에서, **VPC로 격리된 네트워크를 직접 설계하고 최소권한 원칙(Least Privilege)을 적용한 웹 서비스 환경**을 완성합니다.

### 핵심 학습 목표
단순히 콘솔 버튼을 누르는 것이 아니라, **"외부 요청(Packet) → Internet Gateway → Route Table → Subnet → Security Group → EC2(Nginx)"** 로 이어지는 트래픽의 흐름을 논리적으로 추적하고 통제할 수 있는 인프라 엔지니어링 역량을 확보합니다.

### 학습자가 스스로 설명할 수 있어야 하는 5대 핵심 질문
1. VPC, Subnet, Route Table, Internet Gateway가 각각 어떤 역할을 하며 트래픽 흐름이 어떻게 이어지는지 설명할 수 있는가?
2. Security Group과 IAM의 역할 차이를 구분하고, 최소 권한 원칙을 왜/어떻게 적용하는지 설명할 수 있는가?
3. 외부 요청이 EC2 웹 서버까지 도달하기 위해 필요한 3대 설정(라우팅, 퍼블릭 IP, 보안그룹)을 논리적으로 설명할 수 있는가?
4. 오류 발생 시 로그/증상을 근거로 가설을 세우고, 검증 후 조치하는 트러블슈팅(증상→가설→검증→조치→결과→재발방지)을 설명할 수 있는가?
5. 클라우드 과금이 발생하는 대표 요인을 알고, 실습 리소스를 안전하게 정리하는 순서와 이유를 설명할 수 있는가?

---

## 2. 필수 제약 사항 및 금기 규칙

| 구분 | 제약 규격 및 규칙 | 위반 시 영향 |
| :--- | :--- | :--- |
| **리전 (Region)** | 서울 리전 (`ap-northeast-2`) 한정 | 리전 불일치 평가 불가 |
| **비용/계정** | AWS 프리 티어 범위 내 진행 (`t2.micro` 또는 `t3.micro`) | 과금 발생 위험 |
| **루트 계정 금지** | 루트 계정으로 직접 리소스 생성/운영 절대 금지 | 클라우드 보안 거버넌스 위반 |
| **관리자 권한 금지** | IAM 사용자/Role에 `AdministratorAccess` 부여 절대 금지 | 최소권한 원칙(Least Privilege) 위반 |
| **전체 포트 개방 금지** | `0.0.0.0/0`에 대해 0-65535 포트 전체 허용 절대 금지 | 보안 감사 즉시 탈락 |
| **SSH 소스 IP 제한** | SSH(22 포트)는 학습자 본인의 공인 IP (`<내IP>/32`)만 허용 | 무차별 대입 공격(Brute-force) 노출 |
| **HTTP 접근 허용** | HTTP(80 포트)는 `0.0.0.0/0` 전체 허용 | 외부 접속 불가 시 실격 |
| **과금 방지 필수 정리** | 실습 종료 후 EC2, EBS, EIP, IGW, VPC 전수 삭제 확인 | 지속적 과금 발생 |
| **실증 검증 필수 (P-25)** | 브라우저 또는 curl로 `http://<퍼블릭IP>` 200 OK 실증 필수 | 미작동 인프라 탈락 |

---

## 3. 기능 요구사항 상세 명세

### 3-1. 프로젝트 폴더 구조 (의무 준수)
```
B3-1/
├── TASK_SPECIFICATION.md                  ← 과제 공식 요구사항 명세서 (본 파일)
├── README.md                              ← 인프라 구성 명세 및 외부 접속 실증 증빙
├── STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE.md← 실무 인프라 구축/검증 5단계 가이드
├── atifact/                               ← 질(Quality) 중심 심층 설계 & 개념 학습 문서군
│   ├── 01_IMPLEMENTATION_DESIGN_AND_TASKS.md
│   ├── 02_LEARNING_GUIDE_FOR_BEGINNERS.md
│   ├── 03_ARCHITECTURE_AND_TASK_ROADMAP.md
│   ├── 04_ENGINEERING_DECISIONS_AND_TRADE_OFFS.md
│   ├── 05_COMPREHENSIVE_ALGORITHM_AND_CODE_DEEP_DIVE.md
│   ├── 06_EVALUATION_AND_EXECUTION_GUIDE.md
│   ├── 07_IAM_LEAST_PRIVILEGE_POLICY_GUIDE.md
│   └── 08_TROUBLESHOOTING_WAR_ROOM_REPORT.md
├── scripts/
│   ├── deploy_infra.sh                   ← CLI 100% 자동화 인프라 프로비저닝 스크립트
│   └── cleanup_infra.sh                  ← 과금 0% 원클릭 완전 철거 스크립트
├── docs/
│   ├── architecture.png                   ← [필수 1] 아키텍처 다이어그램 (VPC, Subnet, IGW, EC2, SG)
│   ├── troubleshooting.md                 ← [필수 3] 가설-검증 실증 트러블슈팅 보고서
│   └── cleanup-checklist.md               ← [필수 4] 리소스 정리 및 Billing 0원 체크리스트
├── app/
│   ├── nginx.conf                         ← Nginx 웹서버 라우팅 및 헬스체크 설정
│   └── index.html                         ← 웹 서비스 응답 본문 ("OK" 또는 환영 메시지)
└── web_evaluation/                        ← 공식 기술 평가 리포트 대시보드
    └── index.html
```

---

### 3-2. 네트워크 구성 명세 (VPC, Subnet, IGW, Route Table)

| 리소스 | 설정 파라미터 규격 | 비즈니스 설계 의도 |
| :--- | :--- | :--- |
| **VPC** | IPv4 CIDR: `10.0.0.0/16`, DNS 호스트 이름 활성화 | 회사/서비스 전용 독립 사설 네트워크 경계 구축 |
| **Public Subnet** | IPv4 CIDR: `10.0.1.0/24`, AZ: `ap-northeast-2a` | 인터넷과 직접 통신 가능한 256개 IP 대역 확보 |
| **Internet Gateway** | VPC와 1:1 연결 (Attach) | 사설 IP와 공인 IP 간의 주소 변환(1:1 NAT) 관문 |
| **Route Table** | 대상 `0.0.0.0/0` → 타겟 `igw-xxxxxxxx` | 외부 인터넷으로 나가는 모든 트래픽을 IGW로 라우팅 |
| **Subnet Association** | Public Subnet을 위 Route Table에 명시적 연결 | 서브넷 내부 인스턴스가 인터넷 아웃바운드 가능하도록 보장 |

---

### 3-3. 컴퓨팅 및 웹 서버 배포 명세 (EC2 & Nginx)

| 항목 | 규격 | 비고 |
| :--- | :--- | :--- |
| **인스턴스 타입** | `t2.micro` 또는 `t3.micro` | AWS 프리 티어 무료 대상 |
| **운영체제 (AMI)** | Ubuntu Server 22.04 LTS (또는 Amazon Linux 2023) | 최신 보안 패치 및 안정성 |
| **스토리지 (EBS)** | 8 ~ 10 GiB gp3/gp2 | 불필요한 과금 방지 최소 용량 |
| **키페어** | RSA `b3-1-key.pem` 생성 후 안전 보관 | `chmod 400` 권한 설정 필수 |
| **퍼블릭 IP** | 인스턴스 런치 시 자동 할당 (`--associate-public-ip-address`) | 외부에서 접근 가능한 고유 공인 IP 부여 |
| **웹 서버** | Nginx 최신 안정 버전 | 포트 80 리스닝, `/` 및 `/health` 라우팅 |
| **로컬 헬스체크** | `curl -i http://localhost` ➡️ `HTTP 200 OK` | 인스턴스 내부 서비스 정상 기동 확인 |

---

### 3-4. 보안 그룹(Security Group) 인바운드/아웃바운드 규격

```
[인바운드 규칙 (Inbound Rules)]
┌──────────┬──────────┬─────────────────┬──────────────────────────────────────────┐
│ 프로토콜  │ 포트 범위 │ 소스 (Source)    │ 목적 및 제약 조건                         │
├──────────┼──────────┼─────────────────┼──────────────────────────────────────────┤
│ TCP      │ 80       │ 0.0.0.0/0       │ 웹 서비스 외부 공개 (브라우저 접속 허용)    │
│ TCP      │ 22       │ <내 공인 IP>/32 │ 관리자 SSH 원격 접속 한정 (전체 개방 금지) │
└──────────┴──────────┴─────────────────┴──────────────────────────────────────────┘

[아웃바운드 규칙 (Outbound Rules)]
┌──────────┬──────────┬─────────────────┬──────────────────────────────────────────┐
│ ALL      │ ALL      │ 0.0.0.0/0       │ 패키지 설치(apt update) 및 외부 API 통신  │
└──────────┴──────────┴─────────────────┴──────────────────────────────────────────┘
```

---

### 3-5. IAM 최소권한 정책 (Least Privilege Policy) JSON 규격
* 실습에 불필요한 S3, RDS, DynamoDB, IAM 관리 권한은 원천 배제하고, EC2/VPC 인프라 라이프사이클에만 필요한 권한으로 한정:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowVpcAndSubnetLifecycle",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:DescribeVpcs",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:DescribeSubnets",
        "ec2:CreateInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:DescribeInternetGateways",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:CreateRoute",
        "ec2:AssociateRouteTable",
        "ec2:DescribeRouteTables"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowSecurityGroupAndEc2Lifecycle",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:DescribeSecurityGroups",
        "ec2:CreateKeyPair",
        "ec2:DeleteKeyPair",
        "ec2:DescribeKeyPairs",
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*"
    }
  ]
}
```

---

### 3-6. 4대 최종 결과물 상세 규격

1. **아키텍처 다이어그램 1장 (`docs/architecture.png` 또는 pdf)**:
   * 구성 요소 전수 포함: VPC (`10.0.0.0/16`), Public Subnet (`10.0.1.0/24`), IGW, Route Table, EC2, Security Group (80, 22), 트래픽 화살표.
2. **웹 서비스 외부 접속 증빙 1개 (`README.md` + 스크린샷)**:
   * (A) 브라우저 `http://<퍼블릭IP>` 접속 페이지 (예: 200 OK / "OK" / 환영 화면)
   * (B) `GET http://<퍼블릭IP>/health` 호출 결과
   * README.md에 접속 정보 및 URL 명시 + 실제 접속 화면 캡처 포함.
3. **트러블슈팅 보고서 1개 (`docs/troubleshooting.md`)**:
   * 최소 1건 이상에 대해 **증상 → 가설 → 검증 → 조치 → 결과 → 재발방지** 표준 6단계 프레임워크로 작성.
   * 대표 시나리오: 보안그룹 80포트 누락으로 인한 외부 접속 불가 문제 실증.
4. **리소스 정리 체크리스트 1개 (`docs/cleanup-checklist.md`)**:
   * 5대 자원(EC2, EBS 볼륨, Elastic IP, IGW, VPC) 삭제 확인 기록.
   * Billing 대시보드 0원 확인 증빙.

---

### 3-7. 보너스 과제 (선택)
1. **보너스 1 (HTTPS 적용)**:
   * DuckDNS / Freenom 등 무료 서브도메인 연결 후 Let's Encrypt `certbot`으로 SSL 인증서 발급 및 HTTPS 443 암호화 통신 적용.
2. **보너스 2 (Docker 컨테이너 배포)**:
   * EC2 내 Docker 엔진 설치 및 Nginx 웹 컨테이너 런치 (`docker run -d -p 80:80 ...`).
   * 내부 200 OK 검증 + 외부 브라우저 접속 검증 + `docker ps` 스크린샷 2장 포함.

---

## 4. 최종 결과물 점검표

| 산출물 | 파일 경로 | 완료 기준 |
| :--- | :--- | :--- |
| 요구사항 명세서 | `B3-1/TASK_SPECIFICATION.md` | 본 명세서 100% 전수 반영 |
| 심층 설계 아티팩트군 | `B3-1/atifact/` (01~08번 문서) | 배움과 설계의 뎁스 극대화 |
| 아키텍처 다이어그램 | `B3-1/docs/architecture.png` | VPC/Subnet/IGW/EC2/SG 전수 표기 |
| 트러블슈팅 보고서 | `B3-1/docs/troubleshooting.md` | 증상-가설-검증-조치-결과-재발방지 6단계 |
| 과금 방지 체크리스트 | `B3-1/docs/cleanup-checklist.md` | 5대 리소스 완전 삭제 검증 |
| 외부 접속 증빙 문서 | `B3-1/README.md` | 접속 URL, 테스트 결과, 스크린샷 |
| 자동화 스크립트 | `B3-1/scripts/deploy_infra.sh` | 원클릭 프로비저닝 완료 |
| 철거 스크립트 | `B3-1/scripts/cleanup_infra.sh` | 원클릭 자원 완전 회수 |
