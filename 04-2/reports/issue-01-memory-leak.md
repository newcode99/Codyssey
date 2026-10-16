# [BUG] agent-leak-app 실행 중 메모리가 계속 쌓이다가 결국 응답 못 함

**Labels:** `bug`, `memory`, `oom-risk`, `P1-critical`  
**Assignees:** agent-admin  
**Environment:** Ubuntu 24.04 LTS / x86_64 / OrbStack VM (agent-server)

---

## 무슨 일이 있었냐면

앱을 띄워두고 몇 분 지나니까 메모리 사용량이 줄어들 기미 없이 계속 올라가더니
나중엔 아예 새 요청을 처리 못 하는 상태가 됨.

재시작하면 잠깐 괜찮아지는데, 일정 시간이 지나면 또 똑같이 반복됨.
처음엔 서버 문제인 줄 알았는데, 앱 프로세스가 메모리를 반납 안 하고 쌓아두는 게 문제였음.

---

## 환경 정보

| 항목 | 값 |
|------|-----|
| 호스트 | agent-server (OrbStack Ubuntu 24.04 AMD64) |
| 앱 바이너리 | `agent-leak-app-x86` |
| 실행 유저 | `agent-admin` (uid=1000) |
| 실행 시각 | 2026-10-17 02:42:56 KST |
| PID | 8990 (메인 워커 프로세스) |
| MEMORY_LIMIT | 512MB |
| MULTI_THREAD_ENABLE | true |

---

## 어떻게 재현하냐면

```bash
export AGENT_HOME=/home/agent-admin/agent-app
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR=$AGENT_HOME/upload_files
export AGENT_KEY_PATH=$AGENT_HOME/api_keys
export AGENT_LOG_DIR=/var/log/agent-app
export MEMORY_LIMIT=512
export CPU_MAX_OCCUPY=50
export MULTI_THREAD_ENABLE=true

cd $AGENT_HOME
./agent-leak-app &

# 실행 후 메모리 추이 관찰
PID=$(pgrep -f agent-leak-app | tail -1)
watch -n 3 "awk '/VmRSS/{print \$2}' /proc/$PID/status"
```

앱 띄운 직후부터 RSS가 올라가기 시작하고, 트랜잭션 처리 구간에서 특히 급격히 증가함.

---

## 수집한 증거

### /proc/[PID]/status — 메모리 수치

```
VmPeak:    422820 kB   ← 기록된 최고 VSZ
VmSize:    596212 kB   ← 현재 가상 주소 예약 (약 582MB)
VmRSS:      25988 kB   ← 실제 물리 메모리 점유 (약 25MB)
VmSwap:         0 kB
Threads:        3
```

> VSZ가 596MB인데 실제 데이터 처리도 시작하기 전임. 메모리를 미리 왕창 예약해두는 구조로 보임.

### ps aux 출력 (실행 직후 ~30초)

```
USER       PID  %CPU %MEM    VSZ    RSS   TTY  STAT
agent-a+  8990   0.4  0.3  596212 25988   ?   SNl
```

- `S` = sleeping (정상 대기)
- `N` = nice=10 (우선순위 낮춤)
- `l` = 멀티스레드 (Deadlock 섹션에서 다시 다룸)

### 시스템 전체 메모리 (free -m)

```
              total   used   free  shared  buff/cache  available
Mem:           8005    648   7364      37         202       7356
Swap:          9029      0   9029
```

현재 VM 전체 메모리엔 여유가 있지만, 앱이 계속 살아있었다면 RSS가 계속 올라가면서 결국 OOM에 근접했을 것임.

### vmstat 출력 (2초 간격, 3회)

```
procs -----memory------ --swap-- --io-- -system-- -----cpu-----
 r  b  swpd   free  buff  cache  si  so  bi  bo  in  cs us sy id wa
 0  0     0 7583556  56 172136   0   0 1079 367 426   0  3  0 97  0
 0  0     0 7574548  60 190628   0   0 4546   0 417 432  2  1 98  0
 0  0     0 7574548  60 190628   0   0    0   0  32  28  0  0 100  0
```

- si/so = 0 → 스왑 활동 없음 (아직 임계 전)
- 두 번째 줄에서 bi(블록 입력) 4546 → 트랜잭션 시작 시 디스크 I/O 급증

---

## 원인 분석

앱 로그를 보면 `[AgentWorker]`가 트랜잭션 시작 시 `Shared_Memory_A` 블록을 할당하는 패턴이 보임.

```
2026-10-17 02:42:58,214 [WARNING] [AgentWorker] Initializing concurrent transaction processors...
2026-10-17 02:43:03,252 [INFO]    [AgentWorker][Worker-Thread-1] LOCK ACQUIRED: [Shared_Memory_A]. (Holding...)
```

여기서 문제는 두 가지임:

**1) 메모리 블록 사전 예약 (Pre-allocation)**  
앱이 뜨자마자 VSZ 596MB를 예약함. 실제 쓰기 전이라 RSS에 다 잡히지 않지만, 요청이 들어오면서 물리 메모리가 채워지는 구조임.

**2) 메모리 반환 누락 (Free 누락)**  
트랜잭션이 완료되거나 실패해도 `Shared_Memory_A` 블록을 해제하지 않는 것으로 보임. Deadlock 상태에서 락을 들고 있는 채로 멈춰버리기 때문에 해당 블록은 영영 반납이 안 됨.

정리하면:
```
트랜잭션 시작 → 메모리 블록 할당 (LOCK ACQUIRED)
       ↓
  Deadlock 발생 → 락 미반환
       ↓
  다음 트랜잭션 → 새 블록 할당 (기존 것 반환 안 됨)
       ↓
  반복 → RSS 우상향 → 결국 OOM
```

---

## 임시 조치 및 검증

### 단기 조치: 주기적 재시작

```bash
# systemd에 MemoryMax 설정 추가
[Service]
MemoryMax=400M
Restart=on-failure
RestartSec=5
```

메모리가 400MB를 넘으면 cgroup이 강제로 프로세스를 죽이고, systemd가 자동으로 재시작함.
완벽한 해결은 아니지만 장애 지속 시간은 줄일 수 있음.

### 모니터링 명령어

```bash
# RSS 추이를 5초마다 찍어서 누수 패턴 확인
PID=$(pgrep -f agent-leak-app | tail -1)
while true; do
    ts=$(date '+%H:%M:%S')
    rss=$(awk '/VmRSS/{print $2}' /proc/$PID/status 2>/dev/null)
    echo "[$ts] RSS=${rss}kB"
    sleep 5
done
```

### 근본 해결: 코드 수준 수정 필요

`Shared_Memory_A` 블록 할당 후 예외 처리 경로에서도 반드시 `free()` 또는 이에 상응하는 해제 루틴이 호출되어야 함.
특히 Deadlock 상황처럼 비정상 종료 경로에서도 finally 블록 또는 RAII 패턴으로 확실히 회수해야 함.

---

## 참고

- Deadlock과 연계된 문제라 `issue-03-deadlock.md`도 같이 볼 것
- OOM Killer 발동 이력: `dmesg | grep -i 'oom\|killed process'`
- VmSwap > 0 이 되는 시점부터 성능 급락 주의
