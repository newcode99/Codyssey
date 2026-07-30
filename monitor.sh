#!/bin/bash
# ==============================================================================
# monitor.sh - 시스템 상태 수집 및 로깅 스크립트
# 요구사항: Health Check, 방화벽 점검, 리소스 수집(CPU/MEM/DISK), 경고 출력, 로깅
# 소유자: agent-dev | 그룹: agent-core | 권한: 750
# ==============================================================================

# --- [변수 설정] ---
# cron으로 실행될 때는 사용자의 환경 변수(.bashrc)를 읽지 못할 수 있으므로,
# 스크립트 내부에서 핵심 경로를 명시적으로 선언해 주는 것이 매우 안전함.
AGENT_APP_NAME="agent-app"
AGENT_APP_PORT=15034
LOG_FILE="/var/log/agent-app/monitor.log"
LOG_MAX_SIZE=$((10 * 1024 * 1024))  # 10MB
LOG_MAX_FILES=10
WARN_CPU=20
WARN_MEM=10
WARN_DISK=80

# ==============================================================================
# 1. Health Check (실패 시 즉시 종료 exit 1)
# ==============================================================================
echo "====== SYSTEM MONITOR RESULT ======"
echo ""
echo "[HEALTH CHECK]"

# 1-1. 프로세스 확인
# pgrep -f 옵션으로 해당 이름을 가진 프로세스의 PID 추출
PID=$(pgrep -f "$AGENT_APP_NAME")
if [ -z "$PID" ]; then
    echo "[ERROR] 프로세스 '$AGENT_APP_NAME' 실행 중지 상태."
    exit 1
fi
echo "Checking process '$AGENT_APP_NAME'... [OK] (PID: $PID)"

# 1-2. 포트 LISTEN 확인
# ss 출력에서 :15034 가 있는지 검사. -q 는 화면 출력 생략(결과만 참거짓으로 판단)
if ! ss -tlnp | grep -q ":$AGENT_APP_PORT"; then
    echo "[ERROR] 포트 $AGENT_APP_PORT 닫힘 상태."
    exit 1
fi
echo "Checking port $AGENT_APP_PORT... [OK]"


# ==============================================================================
# 2. 상태 점검 (방화벽 - 실패 시 경고만 출력, 스크립트 계속 진행)
# ==============================================================================
echo ""
echo "[FIREWALL STATUS]"
# ufw status 명령 결과 중 'active' 단어가 있는지 검사
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | grep -i "Status" | awk '{print $2}')
    if [ "$UFW_STATUS" = "active" ]; then
        echo "[OK] 방화벽(UFW) 활성화 상태"
    else
        echo "[WARNING] 방화벽(UFW) 비활성 상태!"
    fi
else
    echo "[WARNING] UFW 명령어를 찾을 수 없음 (Docker 환경 제약일 수 있음)"
fi


# ==============================================================================
# 3. 자원 수집 (CPU / Memory / Disk)
# ==============================================================================
echo ""
echo "[RESOURCE MONITORING]"

# CPU 사용률 추출 (top 명령어 1회 실행 후 파싱)
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'.' -f1)
if [ -z "$CPU_USAGE" ]; then CPU_USAGE=0; fi

# MEM 사용률 추출 (free 명령어 파싱, 소수점 1자리)
MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2*100}')
if [ -z "$MEM_USAGE" ]; then MEM_USAGE=0.0; fi

# DISK 사용률 추출 (루트 파티션 기준, % 문자 제거)
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ -z "$DISK_USAGE" ]; then DISK_USAGE=0; fi

echo "CPU Usage : ${CPU_USAGE}%"
echo "MEM Usage : ${MEM_USAGE}%"
echo "DISK Used : ${DISK_USAGE}%"


# ==============================================================================
# 4. 임계값 경고 출력
# ==============================================================================
echo ""
# 정수형으로 비교하기 위해 메모리는 소수점 버림
MEM_USAGE_INT=$(echo "$MEM_USAGE" | cut -d'.' -f1)

if [ "$CPU_USAGE" -gt "$WARN_CPU" ]; then
    echo "[WARNING] CPU threshold exceeded (${CPU_USAGE}% > ${WARN_CPU}%)"
fi

if [ "$MEM_USAGE_INT" -gt "$WARN_MEM" ]; then
    echo "[WARNING] MEM threshold exceeded (${MEM_USAGE}% > ${WARN_MEM}%)"
fi

if [ "$DISK_USAGE" -gt "$WARN_DISK" ]; then
    echo "[WARNING] DISK threshold exceeded (${DISK_USAGE}% > ${WARN_DISK}%)"
fi


# ==============================================================================
# 5. 로그 기록 및 용량 관리 (Log Rotation)
# ==============================================================================
# 파일이 10MB 초과 시 기존 로그를 .1, .2 형태로 미루고 새로 기록
if [ -f "$LOG_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
    if [ "$FILE_SIZE" -gt "$LOG_MAX_SIZE" ]; then
        for i in $(seq $((LOG_MAX_FILES - 1)) -1 1); do
            [ -f "${LOG_FILE}.${i}" ] && mv "${LOG_FILE}.${i}" "${LOG_FILE}.$((i + 1))"
        done
        mv "$LOG_FILE" "${LOG_FILE}.1"
        touch "$LOG_FILE"
    fi
fi

# 로그 라인 생성 및 파일 어펜드 (>>)
# 포맷: [YYYY-MM-DD HH:MM:SS] PID:... CPU:..% MEM:..% DISK_USED:..%
NOW=$(date "+%Y-%m-%d %H:%M:%S")
LOG_TEXT="[$NOW] PID:$PID CPU:${CPU_USAGE}% MEM:${MEM_USAGE}% DISK_USED:${DISK_USAGE}%"

echo "$LOG_TEXT" >> "$LOG_FILE"

echo ""
echo "[INFO] Log appended: $LOG_FILE"
echo "==================================="
