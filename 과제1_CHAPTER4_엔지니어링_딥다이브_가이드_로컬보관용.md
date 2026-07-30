# [DEEP DIVE] 본과제1 CHAPTER4 (agent-app) 인프라 및 보안 엔지니어링 가이드 (로컬 보관용)

본 문서는 `agent-app` 배포 미션에서 사용된 **시스템 설계 원칙, 명령어, 문법, 그리고 특정 기술을 선택한 근거**를 극한의 디테일로 파헤친 엔지니어링 가이드입니다. 어설픈 기계적 명령어 복사가 아닌, 각 요소가 왜 그렇게 동작해야만 하는지에 대한 '이유(Why)'와 '원리(How)'를 영구적으로 보존하기 위해 작성되었습니다.

---

## 1. 인프라 환경 구성: OS 및 아키텍처 선택의 근거

### 1.1. ARM64 vs AMD64 (x86_64) 호환성 문제
- **발생했던 문제**: 초기에 M시리즈 Mac(ARM64) 환경에서 생성된 가상머신으로 `agent-app`을 실행하려 했을 때 `Exec format error` 또는 `GLIBC_2.38 not found` 에러가 발생했습니다.
- **원인 분석 (`ldd`, `file` 명령어)**:
  - `file agent-app` 명령을 통해 해당 바이너리가 `ELF 64-bit LSB executable, x86-64` 포맷임을 확인했습니다. 즉, Intel/AMD 프로세서 아키텍처 전용으로 빌드된 파일이었습니다.
  - 리눅스 커널은 다른 아키텍처의 바이너리를 네이티브로 실행할 수 없으며, 강제로 에뮬레이션 레이어(QEMU 등)를 씌우거나 호환 라이브러리를 설치하면 시스템의 성능 저하 및 알 수 없는 사이드 이펙트(시스템 오염)가 발생합니다.
- **해결 및 선택 이유**: 가상머신(OrbStack) 자체를 **AMD64(x86_64) Ubuntu 24.04** 머신으로 재생성했습니다. 이는 문제를 우회하는 것이 아니라, 애플리케이션이 요구하는 네이티브 런타임 환경을 100% 깔끔하게 제공하는 가장 확실하고 무결한 엔지니어링 결정이었습니다.

---

## 2. 네트워크 및 방화벽 보안 (Systemd & UFW)

### 2.1. SSH 포트 변경 (`20022`)과 Systemd Socket
- **과거의 방식**: 구형 리눅스에서는 `/etc/ssh/sshd_config` 파일에서 `Port 20022`로 바꾸고 `systemctl restart sshd`를 치면 끝났습니다.
- **Ubuntu 24.04의 변화 (Socket-Based Activation)**:
  - 최신 우분투는 메모리 효율을 위해 SSH 데몬을 항상 띄워두지 않고, `systemd`의 **Socket 단위**로 포트 리스닝을 위임합니다. 누군가 포트로 접속을 시도할 때만 sshd 데몬을 깨웁니다.
- **구현 방식 및 명령어**:
  ```bash
  mkdir -p /etc/systemd/system/ssh.socket.d
  cat <<EOF > /etc/systemd/system/ssh.socket.d/port.conf
  [Socket]
  ListenStream=
  ListenStream=20022
  EOF
  systemctl daemon-reload
  systemctl restart ssh.socket
  ```
- **문법 및 선택 이유**:
  - `ListenStream=` (빈 값): 기본 설정되어 있는 22번 포트 바인딩을 **초기화(비우기)**하는 매우 중요한 문법입니다. 이 줄이 없으면 22번과 20022번 둘 다 열려버리는 대참사가 일어납니다.
  - `Drop-in` 방식(`/etc/systemd/system/...`)을 쓴 이유: 패키지 업데이트 시 기본 설정 파일이 덮어씌워져 설정이 날아가는 것을 방지하기 위해 별도의 오버라이드 파일을 생성했습니다.

### 2.2. UFW (Uncomplicated Firewall) 방어막
- **구현 방식**:
  ```bash
  ufw default deny incoming
  ufw allow 20022/tcp
  ufw allow 15034/tcp
  ufw enable
  ```
- **선택 이유**: White-list 방식(기본은 모두 차단, 필요한 것만 허용)을 채택하여, 향후 시스템에 백도어나 악성 프로세스가 깔리더라도 외부로 통신할 수 있는 포트가 열려있지 않아 해킹 피해를 물리적으로 차단합니다.

---

## 3. 계정 권한 체계 (최소 권한의 법칙과 ACL)

시스템 보안의 꽃은 "권한 관리"입니다. Root 권한 탈취를 막고 횡적 이동(Lateral Movement)을 방지하기 위한 정밀한 설계입니다.

### 3.1. 계정 및 그룹 분리 
- **명령어**: `useradd -m -s /bin/bash -c "운영 관리자" agent-admin`
  - `-m`: `/home/agent-admin` 홈 디렉터리를 생성. (없으면 쉘 환경변수 프로필을 쓸 수 없음)
  - `-s /bin/bash`: 기본 쉘을 지정. (미지정 시 기능이 제한된 `sh`가 할당되어 자동완성 등이 불가함)
- **명령어**: `usermod -aG agent-common,agent-core agent-admin`
  - `-a` (append): 기존 속한 그룹을 유지하면서 추가. (이 옵션을 빼먹으면 기존 그룹에서 다 튕겨져 나오는 대형 사고가 발생함)

### 3.2. 정밀 ACL (`setfacl`) 통제
- UGO(User, Group, Other) 방식인 `chmod 770`의 한계: `agent-admin`이 소유하고 `agent-core`가 소유 그룹일 때, `agent-common` 그룹에게는 권한을 줄 방법이 없음 (Other를 열어야 하는데 이는 보안 위반).
- **명령어 및 문법**:
  ```bash
  setfacl -m g:agent-core:rwx /home/agent-admin/agent-app/api_keys
  setfacl -m d:g:agent-core:rwx /home/agent-admin/agent-app/api_keys
  setfacl -m g:agent-common:--- /home/agent-admin/agent-app/api_keys
  ```
  - `-m` (modify): 규칙 추가/수정.
  - `g:그룹명:권한`: 특정 그룹에만 권한을 핀셋으로 할당.
  - `d:` (default): 이 디렉터리 하위에 앞으로 생성될 새로운 파일들도 기본적으로 이 권한을 물려받게 만드는 매우 중요한 설정입니다.
  - `g:agent-common:---`: **명시적 거부(Explicit Deny)**. `agent-core`에 속하지 않은 `agent-common` 유저(예: `agent-test`)가 들어오려는 시도를 하드웨어 수준에서 차단합니다.

---

## 4. 백그라운드 프로세스 및 로깅 자동화 (`monitor.sh` 딥다이브)

가장 복잡한 로직이 들어간 `monitor.sh`의 명령어들을 해부합니다.

### 4.1. 프로세스 수색: `pgrep -f`
- **문법**: `PID=$(pgrep -f "agent-app")`
- **선택 이유**: 기존의 `ps aux | grep agent-app`을 사용하면 쉘에서 실행된 `grep` 프로세스 자체도 문자열 매칭이 되어 결과에 2개의 PID가 나와버립니다. `pgrep -f`는 오직 실행 커맨드라인 자체가 일치하는 순수 프로세스의 PID 하나만 깔끔하게 정수로 리턴하므로 Health Check의 신뢰도를 100%로 올립니다.

### 4.2. 포트 생존 여부: `ss -tlnp`
- **문법**: `ss -tlnp | grep -q ":15034"`
- **선택 이유**:
  - `netstat`은 느리고 커널의 /proc 통계를 읽어옵니다. `ss`는 커널 넷링크(Netlink) 소켓과 직접 통신하여 엄청나게 빠릅니다.
  - `-t` (TCP), `-l` (Listen 상태), `-n` (포트를 이름이 아닌 숫자로 표시), `-p` (어떤 프로세스가 열고 있는지 표시).
  - `grep -q` (Quiet): 화면에 문자열 출력을 완전히 억제하고 오직 쉘의 종료 상태값(Exit Status, 0 또는 1)만 넘겨 `if` 문의 조건식으로 사용되게 만듭니다.

### 4.3. 자원(Resource) 파싱: `awk`, `cut`, `tr`
- **CPU (`top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'.' -f1`)**
  - `top -b` (Batch mode): 윈도우 인터페이스처럼 화면을 새로고침하지 않고 텍스트로 결과를 쭉 뱉습니다. 스크립트에서 top을 쓸 때 필수입니다.
  - `cut -d'.' -f1`: 딜리미터(`.`)를 기준으로 필드를 잘라내어, 소수점을 버리고 첫 번째(정수) 값만 가져옵니다. 쉘 스크립트의 `if` 조건문은 소수점 비교를 지원하지 않기 때문입니다.
- **MEM (`free | grep Mem | awk '{printf "%.1f", $3/$2*100}'`)**
  - `free` 명령어가 뱉는 값 중 `$2`(Total), `$3`(Used)를 직접 실수 연산하여 백분율로 계산합니다.
- **DISK (`df / | tail -1 | awk '{print $5}' | tr -d '%'`)**
  - `tr -d '%'` (Translate Delete): `24%`라는 문자열에서 `%`라는 문자를 아예 삭제해버립니다. `24`라는 순수 정수만 남겨 비교 연산에 사용하기 위함입니다.

### 4.4. 권한 우회의 정수: `sudoers.d` `NOPASSWD`
- **문제점**: 모니터링 스크립트는 `agent-admin`의 크론탭에서 매 분마다 실행되지만, 스크립트 안의 `ufw status` 명령어는 반드시 Root 권한을 요구합니다. 비밀번호를 칠 수 없는 크론 환경에서는 실패합니다.
- **문법 및 파일**: `/etc/sudoers.d/agent-admin` 
  ```text
  agent-admin ALL=(ALL) NOPASSWD: /usr/sbin/ufw status
  ```
- **선택 이유**: 
  - 스크립트 자체를 Root 계정 크론탭으로 옮겨버리면 모든 권한 에러가 해결되지만, 이는 **미친 짓(시스템 무결성 파괴)**입니다. 일개 어플리케이션 스크립트가 시스템 최고 권한으로 실행되다가 해킹당하면 서버 전체가 넘어갑니다.
  - `sudoers`에 핀셋으로 룰을 추가하여, "agent-admin은 비밀번호 없이 `sudo ufw status` 딱 하나만 실행할 수 있고, 다른 sudo는 절대 못한다"라고 박아버렸습니다. 보안성과 편의성(자동화)을 동시에 잡은 마스터피스입니다.

---

> 본 가이드는 추후 어떠한 리눅스/서버 환경을 구축하더라도 동일한 보안 철학과 깊이 있는 쉘 스크립팅을 구현할 수 있도록 작성된 당신만의 로컬 엔지니어링 바이블입니다.
