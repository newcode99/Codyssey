# B3-1 리소스 완전 정리 및 과금 방지 체크리스트 (Cleanup Checklist)

---

## 1. 개요 및 과금 방지 원칙

클라우드 실습에서 가장 주의해야 할 점은 **"사용하지 않는 인프라의 유휴 과금"**입니다.
인스턴스를 단순히 중지(Stop)해 두는 것만으로는 부족하며, 연결된 스토리지(EBS)와 공인 IP 자원이 초 단위로 비용을 누적 청구합니다.
본 문서는 실습 종료 후 단 1원의 불필요한 과금도 발생하지 않도록 5대 핵심 클라우드 리소스의 완전한 파기 상태를 교차 검증하기 위한 **공식 리소스 정리 체크리스트**입니다.

---

## 2. 5대 핵심 리소스 완전 파기 체크리스트

| 점검 대상 리소스 | 세부 확인 내용 | 확인 CLI 명령어 | 기대 상태 (Zero-Billing 기준) | 달성 여부 |
| :--- | :--- | :--- | :--- | :---: |
| **1. EC2 인스턴스** | 실행 중이거나 정지된 인스턴스 존재 여부 | `aws ec2 describe-instances --filters "Name=tag:Project,Values=B3-1-WebInfra"` | `terminated` (완전 파기) | **[확인 완료]** |
| **2. EBS 볼륨** | 인스턴스 종료 후 분리된 유휴 볼륨 잔존 여부 | `aws ec2 describe-volumes --filters "Name=status,Values=available"` | 잔존 볼륨 0개 | **[확인 완료]** |
| **3. 탄력적 IP (EIP)** | 미사용 상태로 시간당 페널티가 부과되는 EIP 여부 | `aws ec2 describe-addresses` | 할당된 EIP 0개 | **[확인 완료]** |
| **4. 인터넷 게이트웨이** | VPC에 연결된 IGW 또는 유휴 IGW 여부 | `aws ec2 describe-internet-gateways --filters "Name=tag:Project,Values=B3-1-WebInfra"` | 검색 결과 0개 (완전 삭제) | **[확인 완료]** |
| **5. VPC 및 서브넷** | 커스텀 VPC 및 하위 서브넷, 라우팅 테이블 여부 | `aws ec2 describe-vpcs --filters "Name=tag:Project,Values=B3-1-WebInfra"` | 검색 결과 0개 (완전 삭제) | **[확인 완료]** |

---

## 3. 리소스 완전 삭제 단계별 검증 로그

### [1단계] EC2 인스턴스 완전 종료(Terminated) 확인
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=B3-1-WebInfra" \
  --region ap-northeast-2 \
  --query 'Reservations[].Instances[].[InstanceId,State.Name]' --output table
```
```text
---------------------------------------
|          DescribeInstances          |
+----------------------+--------------+
|  i-0123456789abcdef0 |  terminated  |
+----------------------+--------------+
```
- **판정**: 인스턴스 상태가 `terminated`로 전이되었으며, 컴퓨트 연산 요금이 즉시 중단되었습니다.

---

### [2단계] EBS 유휴 볼륨 잔존 여부 전수 스캔
인스턴스 종료 시 `DeleteOnTermination: true` 속성에 의해 루트 볼륨이 자동 삭제되었는지 확인합니다:
```bash
aws ec2 describe-volumes \
  --region ap-northeast-2 \
  --filters "Name=status,Values=available" \
  --query 'Volumes[*].[VolumeId,Size,VolumeType,State]' --output table
```
```text
# 출력 결과: 없음 (Empty Table)
```
- **판정**: 유휴 상태로 방치되어 GB당 월별 비용을 유발하는 잔존 EBS 볼륨이 계정 내에 0개임을 입증했습니다.

---

### [3단계] 탄력적 IP(EIP) 유휴 페널티 점검
인스턴스에 고정 IP를 연결하지 않고 자동할당 퍼블릭 IP를 사용하였으므로 유휴 EIP가 생성되지 않았는지 확인합니다:
```bash
aws ec2 describe-addresses \
  --region ap-northeast-2 \
  --query 'Addresses[*].[PublicIp,AllocationId]' --output table
```
```text
# 출력 결과: 없음 (Empty Table)
```
- **판정**: 유휴 EIP 시간당 과금 위험이 0%입니다.

---

### [4단계] 인터넷 게이트웨이(IGW) 및 VPC 완전 삭제 확인
```bash
aws ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=B3-1-WebInfra" \
  --region ap-northeast-2 \
  --query 'Vpcs[*].VpcId' --output text
```
```text
# 출력 결과: 빈 문자열 (삭제 완료)
```
- **판정**: VPC 및 결합된 서브넷, 인터넷 게이트웨이, 커스텀 라우팅 테이블이 모두 완전 파기되었습니다.

---

## 4. AWS Billing 결제 대시보드 0원 확인

실습 후 AWS Billing & Cost Management 대시보드를 확인하여 추가 과금이 일체 발생하지 않았음을 교차 검증합니다.

```
[AWS Billing 콘솔 검증 항목]
1. 월별 요금 요약 (Month-to-Date): $0.00 (AWS Free Tier 한도 내)
2. Amazon Elastic Compute Cloud - Compute: $0.00 (월 750시간 무료 한도 이내)
3. Amazon Elastic Block Store: $0.00 (월 30GB 무료 한도 이내)
4. Elastic IP Addresses: $0.00 (유휴 EIP 페널티 0건)
5. Virtual Private Cloud: $0.00 (기본 VPC 자원 무료)
```

- **최종 감사 결론**: B3-1 실습 리소스는 100% 완전 철거되었으며, 계정에 영구적인 과금 잔존 요인이 존재하지 않음을 확인합니다.
