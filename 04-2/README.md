# 04-2: 시스템 장애 분석 및 이슈 리포트 (Troubleshooting Reports)

이 폴더는 `agent-leak-app-x86`을 실제 서버 환경(Ubuntu 24.04 AMD64)에서 직접 실행하고 모니터링하면서 발견한 3가지 핵심 시스템 장애(Memory Leak, CPU Spike/Latency, Deadlock)의 실제 로그 증거와 GitHub Issue 형태의 기술 리포트를 모아둔 곳입니다.

---

## 📁 폴더 구조

```text
04-2/
├── README.md                          # 전체 개요 및 리포트 안내
├── evidence/
│   └── leak-app-full.log              # 실제 VM에서 앱 실행 시 수집된 전체 원본 로그
└── reports/
    ├── issue-01-memory-leak.md        # [장애 1] 메모리 누수 및 가상 메모리 비정상 점유 분석
    ├── issue-02-cpu-latency.md        # [장애 2] 워커 초기화 구간 CPU 스파이크 및 응답 지연 분석
    └── issue-03-deadlock.md           # [장애 3] 멀티 스레드 간 상호 락 획득 실패(교착 상태) 분석
```

---

## 📋 장애별 핵심 요약

| 구분 | 리포트 파일 | 주요 현상 | 핵심 원인 |
|------|-------------|-----------|-----------|
| **장애 1** | [issue-01-memory-leak.md](reports/issue-01-memory-leak.md) | 메모리가 계속 누적되다가 응답 불가 및 OOM 위험 | 트랜잭션 처리 중 할당된 버퍼/리소스 미해제 및 가상 메모리(VSZ 582MB) 과다 선점 |
| **장애 2** | [issue-02-cpu-latency.md](reports/issue-02-cpu-latency.md) | 앱 부팅 직후 순간적 CPU 19% 급등 및 응답 지연 | 워커 스레드 초기화 루프에서 대기 없이 연산을 집중 수행하여 순간적 레이턴시 유발 |
| **장애 3** | [issue-03-deadlock.md](reports/issue-03-deadlock.md) | 두 워커 스레드가 멈추고 영원히 정지(BLOCKED) | `Worker-Thread-1`과 `Worker-Thread-2`가 서로 다른 순서로 뮤텍스 락을 잡으려다 상호 대기 진입 |

---

## 🔍 수집된 원본 데이터

- [leak-app-full.log](evidence/leak-app-full.log): 가상머신 `agent-server` 환경에서 백그라운드 구동 후 발생한 장애 로그 전문
