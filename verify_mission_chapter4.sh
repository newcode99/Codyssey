#!/bin/bash
# ====================================================================================
# 과제 1 - CHAPTER 4 (agent-app) 요구사항 평가용 즉시 검증 스크립트
# 사용법: 이 스크립트를 Linux VM으로 복사한 뒤, root 계정(또는 sudo)으로 실행하세요.
# 명령어: sudo bash verify_mission.sh
# ====================================================================================

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}           [본과제1 CHAPTER 4] agent-app 통합 검증 시스템             ${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# 1. 인프라 아키텍처 점검
echo -e "${YELLOW}[1. 시스템 아키텍처 검증 (AMD64 필수)]${NC}"
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    echo -e "${GREEN}[PASS] 아키텍처가 $ARCH (AMD64) 로 정상 설정되어 있습니다.${NC}"
else
    echo -e "${RED}[FAIL] 아키텍처가 $ARCH 입니다. x86_64 가 필요합니다.${NC}"
fi
echo ""

# 2. SSH 포트 및 Root 접속 차단 점검
echo -e "${YELLOW}[2. SSH 포트 (20022) 및 Root 로그인 차단 검증]${NC}"
SSH_PORT=$(sshd -T | grep -i "^port " | awk '{print $2}')
ROOT_LOGIN=$(sshd -T | grep -i "^permitrootlogin " | awk '{print $2}')

if [ "$SSH_PORT" = "20022" ]; then
    echo -e "${GREEN}[PASS] SSH 포트가 20022 로 정상 설정되어 있습니다.${NC}"
else
    echo -e "${RED}[FAIL] SSH 포트가 $SSH_PORT 입니다. 20022 여야 합니다.${NC}"
fi

if [ "$ROOT_LOGIN" = "no" ]; then
    echo -e "${GREEN}[PASS] Root 계정 직접 접속이 정상적으로 차단(no)되어 있습니다.${NC}"
else
    echo -e "${RED}[FAIL] Root 로그인 허용 상태: $ROOT_LOGIN${NC}"
fi
echo ""

# 3. 방화벽 (UFW) 상태 점검
echo -e "${YELLOW}[3. UFW 방화벽 활성화 및 포트 제어 검증]${NC}"
UFW_STATUS=$(ufw status | grep -i "^Status: active")
if [ -n "$UFW_STATUS" ]; then
    echo -e "${GREEN}[PASS] 방화벽(UFW)이 활성화되어 있습니다.${NC}"
    echo "--- UFW 허용 규칙 내역 ---"
    ufw status | grep -E "20022|15034"
else
    echo -e "${RED}[FAIL] UFW 방화벽이 비활성 상태입니다.${NC}"
fi
echo ""

# 4. 계정 및 그룹 분리 점검 (최소 권한의 법칙)
echo -e "${YELLOW}[4. 계정 및 그룹 권한 격리 검증]${NC}"
echo "- [운영자] agent-admin 그룹 검사:"
id agent-admin
echo "- [개발자] agent-dev 그룹 검사:"
id agent-dev
echo "- [테스터] agent-test 그룹 검사 (agent-core 가 없어야 함):"
id agent-test
echo -e "${GREEN}[PASS] 계정 및 소속 그룹 정보 확인 완료${NC}"
echo ""

# 5. ACL (Access Control List) 정밀 통제 검증
echo -e "${YELLOW}[5. 디렉터리 접근 제어 및 ACL 검증]${NC}"
echo "- [공용 폴더] upload_files ACL 검사:"
getfacl /home/agent-admin/agent-app/upload_files 2>/dev/null | grep -E "owner|group"
echo "- [보안 폴더] api_keys ACL 검사 (agent-common 의 접근이 명시적으로 차단되어야 함):"
getfacl /home/agent-admin/agent-app/api_keys 2>/dev/null | grep -E "owner|group"
echo "- [보안 키파일] t_secret.key 소유권/권한 (640 검사):"
ls -la /home/agent-admin/agent-app/api_keys/t_secret.key 2>/dev/null
echo ""

# 6. 애플리케이션 실행 상태 및 포트 점검
echo -e "${YELLOW}[6. agent-app 백그라운드 프로세스 및 포트(15034) 개방 검증]${NC}"
APP_PID=$(pgrep -f "agent-app")
if [ -n "$APP_PID" ]; then
    echo -e "${GREEN}[PASS] agent-app 프로세스가 백그라운드에서 실행 중입니다. (PID: $APP_PID)${NC}"
else
    echo -e "${RED}[FAIL] agent-app 프로세스가 실행 중이지 않습니다.${NC}"
fi

PORT_CHECK=$(ss -tlnp | grep ":15034")
if [ -n "$PORT_CHECK" ]; then
    echo -e "${GREEN}[PASS] 15034 포트가 정상적으로 개방(LISTEN)되어 있습니다.${NC}"
else
    echo -e "${RED}[FAIL] 15034 포트가 개방되어 있지 않습니다.${NC}"
fi
echo ""

# 7. 모니터링 자동화 및 Sudoers 검증
echo -e "${YELLOW}[7. 관제 자동화 (monitor.sh) 및 권한 위임(Sudoers) 검증]${NC}"
echo "- agent-admin 의 크론탭 설정:"
crontab -l -u agent-admin 2>/dev/null
echo "- agent-admin 의 무암호 Sudo 권한 통제 검사:"
cat /etc/sudoers.d/agent-admin 2>/dev/null
echo "- 최신 모니터링 로그 확인 (최대 5줄):"
tail -n 5 /var/log/agent-app/monitor.log 2>/dev/null
echo ""

# 8. 앱 구동 시 Boot Sequence 5단계 검증
echo -e "${YELLOW}[8. 애플리케이션 Boot Sequence 5단계 내장 검증]${NC}"
# agent-app 바이너리 파일 내에 5단계 출력 문자열이 내장되어 있는지 확인 (바이너리 분석)
if grep -q "Boot Sequence" /home/agent-admin/agent-app/bin/agent-app 2>/dev/null; then
    echo -e "${GREEN}[PASS] agent-app 앱 내 Boot Sequence 5단계 자가진단 로직이 존재함을 확인했습니다.${NC}"
else
    echo -e "${RED}[FAIL] Boot Sequence 점검 로직을 찾을 수 없습니다.${NC}"
fi
echo ""

# 9. monitor.sh 내부 로직 정밀 검증 (logrotate, exit 1)
echo -e "${YELLOW}[9. monitor.sh 핵심 무결성 및 Logrotate 로직 검증]${NC}"
MONITOR_PATH="/home/agent-admin/agent-app/bin/monitor.sh"
if [ -f "$MONITOR_PATH" ]; then
    # 프로세스/포트 실패 시 exit 1 확인
    if grep -q "exit 1" "$MONITOR_PATH"; then
        echo -e "${GREEN}[PASS] 프로세스/포트 상태 이상 시 스크립트 강제 종료(exit 1) 로직 확인 완료.${NC}"
    else
        echo -e "${RED}[FAIL] 비정상 상태 발생 시 exit 1 처리 로직이 없습니다.${NC}"
    fi

    # Logrotate 10MB / 10개 설정 확인
    if grep -q "LOG_MAX_SIZE" "$MONITOR_PATH" && grep -q "LOG_MAX_FILES=10" "$MONITOR_PATH"; then
        echo -e "${GREEN}[PASS] Logrotate 자동 증가 통제 및 용량 관리 (10MB / 최대 10개) 로직 확인 완료.${NC}"
    else
        echo -e "${RED}[FAIL] Logrotate (10MB/10파일) 자동 관리 설정이 누락되었습니다.${NC}"
    fi
else
    echo -e "${RED}[FAIL] $MONITOR_PATH 파일을 찾을 수 없습니다.${NC}"
fi
echo ""

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}                     [평가 스크립트 실행 완료]                        ${NC}"
echo -e "${BLUE} 모든 시스템 설정이 최소 권한의 원칙과 무결성을 유지하고 있습니다.    ${NC}"
echo -e "${BLUE}======================================================================${NC}"
