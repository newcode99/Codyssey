#!/usr/bin/env bash
# ==============================================================================
# Codyssey B3-1 보너스 과제: Docker 컨테이너 기반 Nginx 웹 서비스 배포 스크립트
# EC2 인스턴스 내부 또는 SSH 원격을 통해 컨테이너 배포 집행
# ==============================================================================
set -euo pipefail

echo "========================================================================"
echo " [BONUS 2] Docker 엔진 설치 및 Nginx 웹 컨테이너 런치"
echo "========================================================================"

# 1. 기존 Nginx 호스트 데몬 중지 (포트 80 충돌 방지)
if systemctl is-active --quiet nginx; then
  echo "[INFO] 기존 호스트 Nginx 데몬을 중지합니다..."
  sudo systemctl stop nginx
  sudo systemctl disable nginx
fi

# 2. Docker 공식 엔진 설치
if ! command -v docker &> /dev/null; then
  echo "[INFO] Docker 엔진을 설치합니다..."
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  sudo systemctl start docker
  sudo systemctl enable docker
  sudo usermod -aG docker "${USER}" || true
fi

# 3. Nginx Docker 컨테이너 런치 (포트 80 바인딩)
echo "[INFO] Nginx 웹 컨테이너를 실행합니다..."
sudo docker rm -f b3-1-web-container 2>/dev/null || true

sudo docker run -d \
  --name b3-1-web-container \
  --restart always \
  -p 80:80 \
  -v /var/www/html:/usr/share/nginx/html:ro \
  nginx:alpine

echo "[SUCCESS] Docker 컨테이너 실행 완료!"
sudo docker ps --filter "name=b3-1-web-container"

# 4. 내부 헬스체크 검증
echo "[INFO] Docker 컨테이너 로컬 헬스체크 수행 중..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health || true)
if [[ "${HTTP_CODE}" == "200" ]]; then
  echo "[VERIFIED] Docker 컨테이너 내부 헬스체크 성공! (HTTP 200 OK)"
else
  echo "[WARNING] HTTP 응답 코드: ${HTTP_CODE}"
fi
