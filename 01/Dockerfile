# 베이스 이미지 지정
# nginx:alpine = nginx 공식 이미지의 alpine(초경량 Linux) 버전
# alpine 기반이라 이미지 크기가 수 MB 수준으로 매우 작음
FROM nginx:alpine

# 이미지 메타데이터 (관리용 정보, 필수 아님)
# 이미지를 만든 사람과 설명을 기록
LABEL maintainer="hwangjeonghyeon"
LABEL description="Custom nginx web server"

# 환경 변수 설정
# 컨테이너 안에서 $APP_ENV 로 접근 가능
# 코드와 설정을 분리하는 목적
ENV APP_ENV=dev

# 내 컴퓨터의 app/ 폴더를 컨테이너 안으로 복사
# 왼쪽: Dockerfile 기준 상대 경로 (내 컴퓨터)
# 오른쪽: nginx가 기본으로 파일을 서빙하는 컨테이너 내부 경로
COPY app/ /usr/share/nginx/html/

# 이 컨테이너가 사용하는 포트 선언 (문서화 목적)
# 실제로 포트를 여는 것이 아님
# 실제 포트 연결은 docker run -p 로 처리
EXPOSE 80
