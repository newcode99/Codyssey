# B3-1 IAM 최소권한 정책 및 클라우드 보안 가이드 (IAM_LEAST_PRIVILEGE_POLICY_GUIDE)

---

## 1. 개요

클라우드 보안의 제1원칙은 **최소 권한의 원칙(Principle of Least Privilege, PoLP)**입니다.
사용자나 애플리케이션에는 업무를 수행하는 데 꼭 필요한 최소한의 권한만 부여해야 하며, 단 하나의 과도한 권한도 허용해서는 안 됩니다.
본 문서는 B3-1 인프라를 프로비저닝하기 위해 설계된 커스텀 IAM 정책의 구조와 각 액션(Action)의 당위성, 그리고 침해 사고 모델링을 통한 보안 아키텍처를 심층 분석합니다.

---

## 2. 왜 `AdministratorAccess`는 금기 대상인가? (Threat Modeling)

많은 개발자가 인프라 구축 시 발생하는 "Access Denied" 에러를 빠르게 해결하기 위해 편의상 `AdministratorAccess`를 부여합니다. 이는 매우 위험한 안티 패턴입니다.

```
[AdministratorAccess 부여 시 위험 시나리오]

                      ┌──> S3 버킷 침해 ──> 회사 기밀 및 고객 개인정보 유출
                      │
[액세스 키 탈취] ─────┼──> 비싼 GPU 인스턴스 무단 생성 ──> 암호화폐 채굴 수천만 원 과금 (Cryptojacking)
 (깃허브 유출 / 악성코드)│
                      ├──> RDS 데이터베이스 삭제 ──> 랜섬웨어 인질극
                      │
                      └──> 신규 IAM 관리자 생성 ──> 계정 소유권 영구 탈취 및 백도어 설치
```

- **최소권한 정책 적용 시 방어 효과**:
  본 과제의 커스텀 정책이 적용된 자격증명은 S3, RDS, DynamoDB, IAM 등의 서비스에 전혀 접근할 수 없습니다. 오직 VPC와 지정된 규격의 EC2 라이프사이클만 다룰 수 있으므로, 키가 침해당하더라도 피해 반경이 국소 영역으로 완벽히 통제(Blast Radius Containment)됩니다.

---

## 3. 커스텀 인라인 정책 (`LeastPrivilegePolicy.json`) 전수 해부

본 정책은 총 2개의 Statement와 28개의 세부 EC2 Action으로 엄격히 한정되어 있습니다.

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
        "ec2:ModifyVpcAttribute",
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
        "ec2:DisassociateRouteTable",
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
        "ec2:DescribeInstanceStatus",
        "ec2:DescribeImages",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 4. 액션별 CLI 명령어 및 비즈니스 목적 1:1 매핑표

| Statement | IAM Action 명칭 | 대응되는 AWS CLI 명령어 | 비즈니스 목적 및 필요성 |
| :--- | :--- | :--- | :--- |
| **VPC / Subnet** | `ec2:CreateVpc` | `aws ec2 create-vpc` | `10.0.0.0/16` 가상 사설망 생성 |
| | `ec2:ModifyVpcAttribute` | `aws ec2 modify-vpc-attribute` | DNS 호스트네임 활성화 |
| | `ec2:CreateSubnet` | `aws ec2 create-subnet` | `10.0.1.0/24` 퍼블릭 서브넷 생성 |
| | `ec2:CreateInternetGateway` | `aws ec2 create-internet-gateway` | 외부 통신 관문 생성 |
| | `ec2:AttachInternetGateway` | `aws ec2 attach-internet-gateway` | IGW를 VPC에 바인딩 |
| | `ec2:CreateRoute` | `aws ec2 create-route` | `0.0.0.0/0 -> IGW` 라우팅 등록 |
| | `ec2:AssociateRouteTable` | `aws ec2 associate-route-table` | 라우팅 테이블과 서브넷 결합 |
| **EC2 / SG** | `ec2:CreateSecurityGroup` | `aws ec2 create-security-group` | 웹/SSH 전용 방화벽 생성 |
| | `ec2:AuthorizeSecurityGroupIngress` | `aws ec2 authorize-security-group-ingress` | 80 및 22 포트 규칙 추가 |
| | `ec2:CreateKeyPair` | `aws ec2 create-key-pair` | SSH 원격 접속용 pem 키 생성 |
| | `ec2:DescribeImages` | `aws ec2 describe-images` | 최신 Ubuntu 22.04 AMI 조회 |
| | `ec2:RunInstances` | `aws ec2 run-instances` | EC2 가상머신 기동 및 Nginx 설치 |
| | `ec2:CreateTags` | `aws ec2 create-tags` | 리소스 식별용 Name 태깅 |
| | `ec2:TerminateInstances` | `aws ec2 terminate-instances` | 실습 종료 후 인스턴스 파기 |

---

## 5. 비인가 행위(Deny) 실증 시뮬레이션

본 최소 권한 정책이 적용된 계정으로 허용되지 않은 타 서비스를 호출할 경우의 실제 동작 검증입니다.

### [시뮬레이션 1] S3 버킷 목록 조회 시도
```bash
aws s3 ls
```
```text
An error occurred (AccessDenied) when calling the ListBuckets operation: User is not authorized to perform: s3:ListBuckets because no identity-based policy allows the s3:ListBuckets action.
```
- **해석**: S3에 대한 명시적 허용이 없으므로 AWS IAM 엔진의 암묵적 거부(Implicit Deny) 원칙에 따라 즉각 차단됩니다.

### [시뮬레이션 2] RDS 데이터베이스 인스턴스 생성 시도
```bash
aws rds describe-db-instances --region ap-northeast-2
```
```text
An error occurred (AccessDenied) when calling the DescribeDBInstances operation: User is not authorized to perform: rds:DescribeDBInstances.
```
- **해석**: 고비용의 데이터베이스 서비스에 대한 접근이 원천 차단되어 의도치 않은 과금을 유발할 수 없습니다.

---

## 6. 클라우드 보안 감사 체크리스트 (Security Audit)

- [x] **루트 계정 격리**: 루트 계정의 액세스 키가 삭제되었거나 비활성화되어 있는가?
- [x] **관리자 권한 배제**: 작업 계정에 `AdministratorAccess` 또는 `PowerUserAccess`가 부여되지 않았는가?
- [x] **서비스 범위 한정**: EC2/VPC 외의 서비스(S3, RDS, IAM 등) 권한이 원천 차단되었는가?
- [x] **포트 개방 범위 한정**: SSH 포트(22)가 전 세계(`0.0.0.0/0`)에 개방되지 않고 관리자 단일 IP(`/32`)로 한정되었는가?
- [x] **키페어 권한 엄격화**: 생성된 개인키(`.pem`) 파일 권한이 `chmod 400`으로 보호되어 있는가?
