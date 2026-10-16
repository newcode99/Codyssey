# [BUG] 앱 시작하자마자 CPU가 껑충 뛰더니 요청 처리가 느려짐

**Labels:** `bug`, `performance`, `cpu`, `P2-high`  
**Assignees:** agent-admin  
**Environment:** Ubuntu 24.04 LTS / x86_64 / OrbStack VM (agent-server)

---

## 무슨 일이 있었냐면

`agent-leak-app`을 띄우고 몇 초가 지나니까 CPU 사용률이 생각보다 높게 잡히기 시작했음.
별로 요청이 없는 상황인데도 프로세스가 CPU를 계속 점유하고, 이 상태에서 실제 클라이언트 요청이 오면 응답이 많이 느려짐.

특히 초기화 단계(트랜잭션 워커 구동 직후)에서 급등이 시작됨.
나중엔 Deadlock 상태로 빠져서 아예 처리를 못 하게 됐는데, 그 직전 구간이 가장 위험함.

---

## 환경 정보

| 항목 | 값 |
|------|-----|
| 호스트 | agent-server (OrbStack Ubuntu 24.04 AMD64) |
| 앱 바이너리 | `agent-leak-app-x86` |
| 실행 방식 | systemd (`agent-leak-app.service`) |
| 실행 유저 | `agent-admin` (uid=1000) |
| 실행 시각 | 2026-10-17 03:04:25 KST |
| Main PID | 11415 (부모), 11427 (워커) |
| CPU_MAX_OCCUPY 설정 | 50% |
| MULTI_THREAD_ENABLE | true |

---

## 어떻게 재현하냐면

```bash
# systemd 서비스로 시작
systemctl start agent-leak-app.service

# 시작 직후 5초마다 CPU 확인
watch -n 1 'ps aux | grep agent-leak | grep -v grep'
```

앱이 뜨고 약 5~7초 뒤에 트랜잭션 워커가 시작되면서 CPU가 올라가기 시작함.
`MULTI_THREAD_ENABLE=true` 상태에서 두 스레드가 동시에 CPU를 잡으면서 부하가 생김.

---

## 수집한 증거

### CPU 시계열 (ps aux, 5초 간격)

```
[03:04:40] PID=11415  CPU=11.3  MEM=0.0  STATE=Ss
           PID=11427  CPU=8.1   MEM=0.3  STATE=SNl

[03:04:45] PID=11415  CPU=9.4   MEM=0.0  STATE=Ss
           PID=11427  CPU=6.2   MEM=0.3  STATE=SNl

[03:04:50] PID=11415  CPU=7.1   MEM=0.0  STATE=Ss
           PID=11427  CPU=4.3   MEM=0.3  STATE=SNl

[03:04:55] PID=11415  CPU=5.2   MEM=0.0  STATE=S
           PID=11427  CPU=2.1   MEM=0.3  STATE=SNl

[03:05:00] PID=11415  CPU=0.3   MEM=0.0  STATE=S
           PID=11427  CPU=0.0   MEM=0.3  STATE=SNl
```

- 초반 11.3% + 8.1% → 합산 약 **19.4%** 점유
- 이후 Deadlock 진입하면서 CPU는 떨어졌지만 그게 더 위험한 상황 (처리 자체가 멈춘 것)

### ps aux 상태 코드 해석

```
STATE = SNl
  S → sleeping (일반 대기)
  N → nice=10 (우선순위를 낮게 설정함 — [SafetyGuard] 로그에서 확인)
  l → 멀티스레드 (l = multi-threaded)
```

앱이 스스로 `nice=10`으로 우선순위를 낮췄는데도 CPU가 높게 잡힘.
그만큼 초기 트랜잭션 처리가 CPU를 많이 씀.

### systemd cgroup 통계

```
● agent-leak-app.service
   Active: active (running) since 03:04:25 KST; 12s ago
   Memory: 37.0M (peak: 37.0M)
   CPU:    2.308s
```

12초 실행에 CPU 시간 2.3초 사용 → 평균 19% 점유율과 일치함.

### 앱 로그 — CPU 집중 구간 특정

```log
2026-10-17 03:04:27,401 [INFO] [SafetyGuard] Process priority lowered (nice=10).
2026-10-17 03:04:27,407 [INFO] Agent listening at port 15034

2026-10-17 03:04:29,425 [WARNING] [AgentWorker] Initializing concurrent transaction processors...
2026-10-17 03:04:29,429 [WARNING] [System] CAUTION: Strict resource locking is enabled.
                               ↑
                         여기서 CPU 급등 시작

2026-10-17 03:04:34,640 [INFO] [Worker-Thread-1] Process Started. Attempting to lock [Shared_Memory_A]...
2026-10-17 03:04:34,642 [INFO] [Worker-Thread-2] Process Started. Attempting to lock [Socket_Pool_B]...
```

`Initializing concurrent transaction processors` 이후 약 5초 만에 두 스레드가 동시에 뜨면서 CPU 부하가 집중됨.

### top 출력 (실행 12초 시점)

```
top - 03:04:37
Tasks: 54 total, 1 running, 22 sleeping, 31 zombie
%Cpu(s): 11.0 us, 3.0 sy, 0.0 ni, 86.0 id, 0.0 wa

  PID  USER    PR  NI    VIRT    RES    SHR S  %CPU  %MEM
11415  agent+  30  10  420772   3960   1200 S  11.3   0.0  agent-leak-app
11427  agent+  30  10  596200  26032   4800 S   8.1   0.3  agent-leak-app
```

---

## 원인 분석

앱 로그와 수치를 같이 보면 원인 구조가 명확히 보임.

**구조적인 문제:**

```
[AgentWorker] 초기화 시작
    ↓
Thread-1, Thread-2 동시 생성 (concurrent mode)
    ↓
각 스레드가 동시에 리소스 락 시도 → CPU 집중
    ↓
락을 쥐고 다음 리소스 기다리는 동안 spin-wait 또는 타이트한 loop 실행
    ↓
CPU는 올라가고, 실제 처리는 안 됨 → Latency 증가
```

핵심은 두 가지임:

1. **동시 스레드가 동시에 락을 시도함** → CPU 경합 발생  
2. **락 대기 중에 busy-wait 패턴이 있는 것으로 추정** → sleep/yield 없이 계속 CPU를 씀

`nice=10`으로 우선순위를 낮췄지만, CPU 경합이 심한 구간에서는 system CPU까지 함께 올라가기 때문에 다른 프로세스에도 영향을 줄 수 있음.

---

## 임시 조치 및 검증

### 단기: CPU 제한 설정 (cgroup)

```bash
# systemd 유닛에 CPU 상한 추가
[Service]
CPUQuota=30%
```

이렇게 하면 단일 프로세스가 CPU 30% 이상 쓰는 걸 cgroup 레벨에서 막을 수 있음.
응답 속도는 조금 더 느려질 수 있지만, 다른 서비스에 영향을 주지 않음.

### 모니터링 명령어

```bash
# CPU 점유 실시간 확인
watch -n 1 'ps aux --sort=-%cpu | head -5'

# 5초 간격으로 찍어서 파일에 저장
while true; do
    echo "[$(date '+%H:%M:%S')] $(ps aux | grep agent-leak | grep -v grep | awk '{print "PID="$2" CPU="$3"%"}')"
    sleep 5
done >> /var/log/agent-app/cpu_trace.log
```

### 근본 해결

`concurrent transaction processors` 초기화 로직에서 스레드를 순차적으로 띄우거나,
각 스레드의 락 시도 사이에 `time.sleep()` 또는 backoff 로직을 추가해야 함.
두 스레드가 동시에 서로 다른 락을 쥐고 서로의 것을 기다리는 구조 자체가 근본 문제 (→ Deadlock 이슈 참고).

---

## 참고

- Deadlock과 직접 연결된 문제 → `issue-03-deadlock.md` 반드시 같이 확인
- Memory 이슈도 동시 발생 → `issue-01-memory-leak.md` 참고
- CPU spike 발생 시간대: `2026-10-17 03:04:29 ~ 03:04:36` (약 7초 구간)
