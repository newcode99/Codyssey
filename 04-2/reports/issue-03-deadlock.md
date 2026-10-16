# [BUG] 두 스레드가 서로 기다리다가 앱이 완전히 먹통이 됨 (Deadlock)

**Labels:** `bug`, `deadlock`, `concurrency`, `P1-critical`  
**Assignees:** agent-admin  
**Environment:** Ubuntu 24.04 LTS / x86_64 / OrbStack VM (agent-server)

---

## 무슨 일이 있었냐면

`MULTI_THREAD_ENABLE=true` 상태로 앱을 켜면, 시작하고 몇 초 후에 트랜잭션 처리가 완전히 멈춤.
로그는 멀쩡히 나오고 있고, 포트도 열려있고, 프로세스도 살아있는데 아무것도 처리가 안 됨.

처음에 그냥 느린 건 줄 알았는데, 보니까 두 스레드가 서로 상대방이 갖고 있는 걸 기다리느라 둘 다 완전히 멈춰버린 것이었음.
이게 Deadlock임. 한 번 빠지면 외부에서 강제로 재시작하기 전까지 스스로 빠져나오질 못함.

---

## 환경 정보

| 항목 | 값 |
|------|-----|
| 호스트 | agent-server (OrbStack Ubuntu 24.04 AMD64) |
| 앱 바이너리 | `agent-leak-app-x86` |
| 실행 방식 | systemd (`agent-leak-app.service`) |
| 실행 유저 | `agent-admin` (uid=1000) |
| 실행 시각 | 2026-10-17 03:04:25 KST |
| Main PID | 11415, Worker PID | 11427 |
| MULTI_THREAD_ENABLE | **true** ← 핵심 조건 |

---

## 어떻게 재현하냐면

```bash
# MULTI_THREAD_ENABLE=true 상태에서 반드시 재현됨
export MULTI_THREAD_ENABLE=true
systemctl start agent-leak-app.service

# 시작 후 약 7~10초 뒤에 아래 로그가 찍히면 Deadlock 진입
journalctl -u agent-leak-app.service -f | grep -E 'BLOCKED|WAITING|LOCK'
```

앱이 뜰 때마다 100% 재현됨. 타이밍만 조금씩 다를 뿐, 항상 Deadlock 진입.

---

## 수집한 증거

### 앱 로그 — Deadlock 진입 전체 흐름

```log
# 앱 정상 기동
2026-10-17 03:04:27,401 [INFO]    [SafetyGuard] Process priority lowered (nice=10).
2026-10-17 03:04:27,407 [INFO]    Agent listening at port 15034

# 워커 초기화 — 이 시점에 이미 경고 메시지가 나옴
2026-10-17 03:04:29,425 [WARNING] [AgentWorker] Initializing concurrent transaction processors...
2026-10-17 03:04:29,429 [WARNING] [System] CAUTION: Strict resource locking is enabled.

# 두 스레드 동시 실행 시작 (03:04:34)
2026-10-17 03:04:34,640 [INFO] [Worker-Thread-1] Process Started. Attempting to lock [Shared_Memory_A]...
2026-10-17 03:04:34,642 [INFO] [Worker-Thread-2] Process Started. Attempting to lock [Socket_Pool_B]...

# 각자 원하는 락 획득 성공
2026-10-17 03:04:34,657 [INFO] [Worker-Thread-1] LOCK ACQUIRED: [Shared_Memory_A]. (Holding...)
2026-10-17 03:04:34,659 [INFO] [Worker-Thread-2] LOCK ACQUIRED: [Socket_Pool_B]. (Holding...)

# 각자 작업 진행
2026-10-17 03:04:34,666 [INFO] [Worker-Thread-1] Processing critical data in Memory A...
2026-10-17 03:04:34,667 [INFO] [Worker-Thread-2] Establishing network connections in Pool B...

# ⚠️ 2초 후 — 서로 상대방의 락이 필요해짐
2026-10-17 03:04:36,717 [INFO] [Worker-Thread-1] Need resource [Socket_Pool_B] to finish job.
2026-10-17 03:04:36,725 [INFO] [Worker-Thread-2] Need resource [Shared_Memory_A] to write logs.

# 💀 완전 교착 진입
2026-10-17 03:04:36,730 [INFO] [Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
2026-10-17 03:04:36,730 [INFO] [Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)
```

**이 시점 이후로 앱은 아무 로그도 찍지 않음. 완전 정지.**

### Deadlock 구조 도식

```
Thread-1이 가진 것:   [Shared_Memory_A] ← Thread-2가 원하는 것
Thread-2가 가진 것:   [Socket_Pool_B]   ← Thread-1이 원하는 것

Thread-1: "Socket_Pool_B 줘" → Thread-2한테 달라고 기다림
Thread-2: "Shared_Memory_A 줘" → Thread-1한테 달라고 기다림

→ 서로 상대방이 락을 놓길 기다리지만, 둘 다 안 놓음
→ 영원히 대기
```

### ps aux — 교착 진입 후 프로세스 상태

```
USER       PID  %CPU %MEM    VSZ    RSS  STAT COMMAND
agent-a+  11415  0.3  0.0  420772   3960  Ss   agent-leak-app (부모)
agent-a+  11427  0.0  0.3  596200  26032  SNl  agent-leak-app (워커)
```

- CPU가 0%에 가깝게 떨어짐 → 처리가 완전히 멈춘 것
- 프로세스 자체는 살아있어서 systemd가 죽은 줄 모름 (Restart=no 설정이라 재시작도 안 됨)

### /proc/[PID]/task 스레드별 상태

```
TID 11415 → State: S (sleeping) | wchan: do_wait
```

- `do_wait`: 자식 프로세스/스레드를 기다리는 커널 상태
- 부모 스레드가 두 워커 스레드가 끝나길 기다리고 있지만, 그 워커들이 서로 기다리며 멈춰있음

### 포트 상태

```
LISTEN  0   1   0.0.0.0:15034   users:(("agent-leak-app", pid=11427, fd=6))
```

포트는 살아있음. 겉으로는 정상처럼 보이지만 안에서 처리가 완전히 멈춘 상태.
모니터링 도구가 포트만 체크하면 장애를 놓칠 수 있음.

---

## 원인 분석

Deadlock이 발생하려면 아래 4가지 조건이 모두 충족되어야 함.
이번 케이스는 4가지 전부 해당됨.

| 조건 | 이번 케이스에서 해당 여부 |
|------|--------------------------|
| 상호 배제 (Mutual Exclusion) | 각 락은 한 번에 하나의 스레드만 보유 가능 | ✅ |
| 점유 대기 (Hold and Wait) | 락을 쥔 채로 다른 락을 기다림 | ✅ Thread-1은 Memory_A 쥐고 Pool_B 기다림 |
| 비선점 (No Preemption) | 락은 스스로 놔주기 전까지 빼앗을 수 없음 | ✅ |
| 순환 대기 (Circular Wait) | Thread-1 → Pool_B 요청 → Thread-2 보유 → Thread-2 → Memory_A 요청 → Thread-1 보유 | ✅ |

**결국 설계 상의 문제임.** 두 스레드가 서로 다른 순서로 락을 잡는 구조여서 항상 교착이 발생함.

쉽게 말하면:
- Thread-1: 냉장고 문 열고 → 전자레인지 문 열려고 기다림
- Thread-2: 전자레인지 문 열고 → 냉장고 문 열려고 기다림

둘 다 손에 뭔가 들고 있고, 상대방이 놓기를 기다리는 상황.

---

## 임시 조치 및 검증

### 단기: 타임아웃으로 deadlock 감지 후 강제 재시작

```bash
# systemd 유닛에 추가
[Service]
Restart=always
RestartSec=10
TimeoutStartSec=30
```

30초 내에 처리가 없으면 systemd가 재시작함. 완벽하진 않지만 서비스 다운 시간을 최소화할 수 있음.

### 단기: 외부에서 응답 여부 체크하는 헬스체크 추가

```bash
# 포트는 열려있지만 실제 응답이 없으면 재시작
# /etc/systemd/system/agent-leak-app-watchdog.service
ExecStartPost=/bin/bash -c 'sleep 15 && nc -z localhost 15034 || systemctl restart agent-leak-app'
```

포트 열려있는 것만으로는 부족하고, 실제 응답(TCP handshake 이상)을 확인해야 함.

### 검증 방법

```bash
# Deadlock 진입 여부 실시간 확인
journalctl -u agent-leak-app.service -f | grep -E 'BLOCKED|WAITING'

# 로그가 10초 이상 안 나오면 Deadlock 진입 의심
# (정상 상태에서는 주기적으로 로그가 찍혀야 함)
```

### 근본 해결: 락 순서 통일

코드 레벨에서 반드시 **락을 항상 같은 순서로 획득**하도록 수정해야 함.

```
# 잘못된 현재 구조
Thread-1: Memory_A 먼저 → Pool_B 다음
Thread-2: Pool_B 먼저 → Memory_A 다음

# 올바른 구조 (락 순서 통일)
Thread-1: Memory_A 먼저 → Pool_B 다음
Thread-2: Memory_A 먼저 → Pool_B 다음
```

둘 다 같은 순서로 락을 잡으면 Thread-1이 먼저 두 개 다 잡고 처리한 다음
Thread-2가 차례를 기다리게 됨. 교착이 생길 수가 없음.

또는 `tryLock()` + 타임아웃으로 락 획득 실패 시 스스로 물러나는 방식도 가능함.

---

## 참고

- 앱 시작 시 이미 경고가 나옴: `SYSTEM WARNING: POTENTIAL DEADLOCK IN CONCURRENT MODE.`
  → 설계 단계에서 이미 알고 있던 문제인 것으로 보임
- Memory Leak도 이 Deadlock 때문에 악화됨 → `issue-01-memory-leak.md` 참고
- CPU Spike도 Deadlock 직전 구간에서 발생 → `issue-02-cpu-latency.md` 참고
- `MULTI_THREAD_ENABLE=false`로 실행하면 Deadlock은 피할 수 있지만, 처리 성능 저하 감수해야 함
