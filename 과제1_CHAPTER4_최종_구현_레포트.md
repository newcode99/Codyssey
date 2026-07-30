## 🎯 [통합 레포트] 미션 요구사항 100% 매핑 및 구현 상세 검증

### 1️⃣ [인프라 및 시스템 환경 구성]
- **요구사항**: `agent-app`을 실행할 수 있는 리눅스 환경 구성
- **구현 방식**: `orbstack`을 이용해 **Ubuntu 24.04 (AMD64)** 환경의 `agent-server` 구축. 
- **진행 근거 및 추론**: 처음엔 ARM64 환경에서 진행했으나, `agent-app` 바이너리가 `GLIBC 2.38` 이상을 요구하는 `x86_64` 포맷임을 `ldd` 추적으로 확인했습니다. 무리하게 라이브러리를 오염시키는 대신, 네이티브 호환성을 100% 보장하는 AMD64 가상머신을 재생성하여 근본적인 원인을 완벽하게 해결했습니다.

### 2️⃣ [네트워크 및 방화벽 보안 (SSH/UFW)]
- **요구사항 1**: SSH 포트를 `20022`로 변경하고, 외부의 무작위 접근을 막을 것.
- **요구사항 2**: Root 계정의 직접 SSH 접근을 원천 차단(`PermitRootLogin no`)할 것.
- **요구사항 3**: UFW 방화벽을 활성화하여 `20022/tcp(SSH)`와 `15034/tcp(App)` 포트 외 모든 인바운드를 차단할 것.
- **구현 방식 및 근거**:
  - `sshd_config` 수정뿐만 아니라, **Ubuntu 24.04의 systemd 소켓 기반(socket-based activation) 특성**을 자가 추론하여 파악했습니다. 단순 데몬 재시작으로는 포트가 바뀌지 않음을 인지하고, `/etc/systemd/system/ssh.socket.d/port.conf` Drop-in 파일을 직접 생성하여 20022 포트 바인딩을 이룩했습니다.
  - 방화벽 설정 중 UFW 룰을 최소 단위로 개방하고 기본 정책을 Deny로 설정하여 무결성을 지켰습니다.
- **테스트 결과**: `sshd -T` 명령과 `ufw status`를 통해 20022, 15034 허용 및 Root 접속 차단 적용 완료됨을 실측 **[PASS]**

### 3️⃣ [계정 및 그룹의 최소 권한 분리]
- **요구사항**: `agent-admin`(운영), `agent-dev`(개발), `agent-test`(테스트) 계정을 생성하고 패스워드를 부여. 
- **요구사항**: `agent-common`, `agent-core` 그룹을 생성. `admin/dev`는 양쪽 모두에, `test`는 `common` 그룹에만 소속시킬 것.
- **구현 방식 및 근거**: 
  - `useradd -m -s /bin/bash` 명령어로 홈 디렉터리와 셸을 안정적으로 매핑했고, `usermod -aG`를 통해 논리적 그룹 계층을 완벽히 나눴습니다.
  - 이로써 각 계정은 목적 외의 행위나 데이터 접근이 불가능하게 되어 **최소 권한 원칙(Principle of Least Privilege)**이 확보되었습니다.
- **테스트 결과**: `id agent-test` 조회 시 `core` 그룹이 빠진 채 `common` 그룹만 할당된 것을 확인 **[PASS]**

### 4️⃣ [디렉터리 구조 및 정밀 ACL 통제]
- **요구사항 1**: `$AGENT_HOME` 산하에 `upload_files`, `api_keys`, `bin` 디렉터리 구성.
- **요구사항 2**: 시스템 로그 경로에 `/var/log/agent-app` 구성.
- **요구사항 3**: `upload_files`는 `common` 그룹이 모두 R/W 가능. 
- **요구사항 4**: `api_keys` 및 `log` 폴더는 `core` 그룹만 R/W 가능, `test` 계정은 절대 접근 불가.
- **구현 방식 및 근거**:
  - 기본 UGO 권한만으로는 디테일한 접근 차단이 어렵기 때문에 **`setfacl` (Access Control List)**을 사용했습니다.
  - `upload_files`에는 `g:agent-common:rwx`를 주입하고, `api_keys`에는 `g:agent-core:rwx` 부여 후 명시적으로 `g:agent-common:---`를 덮어씌워 방어막을 2중으로 쳤습니다.
  - 상위 디렉터리(`/home/agent-admin`)에 `g:agent-common:x` 권한을 주어 내부로 진입은 하되, 소유자가 아니면 `ls`는 불가능하도록 설계했습니다.
- **테스트 결과**: `agent-test` 계정으로 `upload_files` 쓰기 성공, `api_keys` 접근 시도 시 `Permission Denied` 발생 확인 **[PASS]**

### 5️⃣ [환경 변수 영구 등록 및 키 파일 구성]
- **요구사항**: `AGENT_HOME`, `AGENT_PORT`, `AGENT_UPLOAD_DIR`, `AGENT_KEY_PATH`, `AGENT_LOG_DIR` 5개 변수 등록.
- **요구사항**: `t_secret.key`에 `agent_api_key_test` 문자열 삽입 후 `640` 권한 부여.
- **구현 방식 및 근거**:
  - 시스템 전역 오염을 막기 위해 전역(`/etc/profile`)이 아닌 `agent-admin` 계정의 `~/.bashrc` 하단에만 안전하게 `export` 처리했습니다. 
  - `t_secret.key`를 `640` (`rw-r-----`)으로 묶어 소유자(admin)와 소유그룹(core) 외에는 시스템 상의 어떠한 유저도 읽을 수 없게 원천 차단했습니다.
- **테스트 결과**: 앱 기동 시 환경변수 인식을 통해 Boot Check `[2/5] Environment Variables` 및 `[3/5] Required Files` 통과 **[PASS]**

### 6️⃣ [애플리케이션 무중단 가동]
- **요구사항**: `agent-app`을 백그라운드로 실행하고, 15034 포트 Listen 및 정상 상태 생존 여부 점검.
- **구현 방식 및 근거**:
  - `nohup ./agent-app > /dev/null 2>&1 &` 형태로 묶어, 셸 세션이 끊겨도 백그라운드 프로세스로 생존하도록 했습니다. 
  - Root가 아닌 `agent-admin` 권한으로 프로세스를 기동하여, 만약 서버가 해킹당해도 Root 권한이 탈취되지 않는 격리 구조를 완성했습니다.
- **테스트 결과**: `ss -tlnp | grep 15034` 명령어로 LISTEN 상태 정상 확인 완료, 메모리(`+25MB`) 증분 로깅이 출력됨 확인 **[PASS]**

### 7️⃣ [Cron 관제 자동화 (모니터링 스크립트)]
- **요구사항**: `ss`, `ufw status`, `ps`, `df`의 결과를 `/var/log/agent-app/monitor.log`에 저장하는 `monitor.sh` 1분 주기 동작.
- **구현 방식 및 근거 (가장 고도화된 설계 포인트)**:
  - 스크립트 작성 시 가장 큰 논제는 **"일반 계정(`agent-admin`)이 어떻게 Root 명령어인 `ufw status`를 권한 충돌 없이 실행하는가"**였습니다.
  - 이를 해결하기 위해 크론탭을 Root에 올리는 쉬운 길(일관성 파괴)을 버리고, `/etc/sudoers.d/agent-admin`에 `NOPASSWD: /usr/sbin/ufw status` 단 한 줄만 주입했습니다. 
  - 결과적으로 `agent-admin`은 **UFW 상태 조회 이외의 다른 Root 권한은 절대 획득할 수 없는(최소 권한의 법칙)** 100% 무결성 상태에서 모니터링 자동화를 달성했습니다.
- **테스트 결과**: 1분 경과 후 `monitor.log` 파일에 방화벽 정책, 상위 자원 프로세스, 디스크 사용량 내역이 100% 누적 로깅됨을 실시간으로 확인 **[PASS]**

