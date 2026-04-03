# AI/SW 개발 워크스테이션 구축 리포트

본 프로젝트는 비개발자 환경에서 가장 이상적인 개발 환경을 구성하기 위해 Linux 터미널, Docker 엔진, Git 협업 툴의 핵심 원리를 이해하고 직접 재현 가능한 인프라를 구축한 기술 문서입니다.

---

## 1. 실행 환경 및 아키텍처 설계
*   **OS**: macOS (Apple Silicon)
*   **Shell**: `zsh`
*   **Git**: Apple Git-154 (2.39.5)
*   **Docker**: Docker version 28.5.2 (OrbStack 엔진)

**[디렉토리 구조 설계 기준]**
"환경의 격리와 역할의 분리"를 원칙으로 폴더를 구성했습니다. 정적 웹 사이트의 소스코드(Static Assets)를 담당하는 `app/` 디렉토리와 내부 설정 문서들을 `01` 패키지 안에 논리적으로 격리했으며, 프로젝트 최상단에는 인프라 설계도인 `Dockerfile`과 통합 가이드인 `README.md`를 배치하여 버전 관리가 명확해지도록 구조화했습니다.

---

## 2. 터미널 제어 및 리눅스 시스템 기초 (Linux CLI)

### 2.1 절대 경로와 상대 경로의 활용
CLI 환경에서 목표 디렉토리로 이동하거나 명령을 수행할 때 두 가지 경로 표기법을 목적에 맞게 혼용했습니다.
*   **상대 경로 (`./` 또는 `../`)**: 현재 워킹 디렉토리 내에서 코드 모듈을 참조하거나 근거리 폴더로 빠르게 접근할 때 활용합니다.
*   **절대 경로 (`/Users/hwang/...`)**: 루트 경로(`/`)부터 시작하는 변하지 않는 주소로써, 컨테이너 볼륨과 호스트를 바인딩(`-v`)할 때 경로 이탈에 의한 마운트 실패를 원천 차단하기 위해 사용합니다.

### 2.2 디렉토리 제어 및 파일 권한(Permission) 체계 검증
터미널에서 기초 명령어를 사용하여 디렉토리를 구축하고, 리눅스 권한 체계의 보안성을 검증했습니다.
```bash
$ pwd
/Users/hwangjeonghyeon/practice/python-practice
$ mkdir test
$ ls -la
01    test
```
리눅스의 파일 권한은 8진수 숫자로 오너/그룹/기타 권한을 제어합니다. 각각 **4(읽기), 2(쓰기), 1(실행)** 의 2진 비트 합산으로 도출됩니다. 아래는 `rwx`(7) 상태였던 폴더를 `644`(rw-r--r--)로 억제하여 디렉토리 접근 시뮬레이션을 수행한 로그입니다.
```bash
$ chmod 644 test
$ ls -ld test
drw-r--r--  2 hwangjeonghyeon  staff  64 Apr  2 23:06 test
```

---

## 3. Docker 인프라 생명주기 및 네트워크 구성

### 3.1 Docker 데몬 확인 및 기반 컨테이너 실행
로컬의 Docker 상태를 점검하고, 독립된 격리망이 런타임에 문제없이 구동되는지 공식 `hello-world` 이미지를 통해 검증했습니다.
```bash
$ docker info
Server Version: 28.5.2 \ Operating System: OrbStack \ CPUs: 8 \ Total Memory: 7.808GiB

$ docker run hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

### 3.2 이미지와 컨테이너의 기술적 차이 및 빌드
*   **이미지 (Build 관점)**: OS와 소스가 층층이 결합된 읽기 전용(Read-Only)의 '불변 템플릿(설계도)' 입니다. 
*   **컨테이너 (Run 관점)**: 위 이미지를 메모리에 띄워 생명력을 부여한 '실행 중인 프로세스 인스턴스' 입니다. 컨테이너 내부에서 발생한 파일 변경은 원본 이미지에 반영되지 않으므로 영구적 변경을 원한다면 아래처럼 무조건 Dockerfile을 통해 새 이미지로 재빌드해야 합니다.

**[Nginx 커스텀 웹 서버 빌드 증명]**
```dockerfile
# Dockerfile
FROM nginx:alpine
LABEL maintainer="hwangjeonghyeon"
COPY app/ /usr/share/nginx/html/
EXPOSE 80
```
```bash
$ docker build -t my-web:1.0 .
```

### 3.3 네트워크 격리 개방 및 포트 매핑 (Port Mapping)
컨테이너는 커널의 Network Namespace에 의해 호스트와 독립된 사설 IP 대역망을 형성하므로 외부에서 직접 접근할 수 없습니다. 따라서 호스트의 특정 포트(예: 8080)로 통신이 밀려들 때 이를 컨테이너망 내부 포트(80)로 포워딩 연결해주는 NAT 기능이 핵심입니다. 이를 누구나 즉시 재현할 수 있도록 구문을 정형화했습니다.
```bash
$ docker run -d -p 8080:80 --name my-web-8080 my-web:1.0
```
![포트 매핑 증명 완료](./01/images/port-map.png)

---

## 4. 데이터 영속성 (Data Persistence) 및 스토리지 관리

컨테이너가 파괴(rm)될 때 휘발성 레이어도 함께 소멸하여 데이터 유실이 발생할 수 있습니다. 이를 방지하기 위한 2가지 대안 장치를 모두 테스트했습니다.
1.  **바인드 마운트 (Bind Mount)**: 호스트의 폴더를 컨테이너 경로에 거울처럼 비춰, 개발 중인 소스코드의 핫 리로딩(Live update)을 지원합니다.
    ```bash
    $ docker run -d -p 8081:80 --name my-web-mount -v $(pwd)/app:/usr/share/nginx/html my-web:1.0
    ```
2.  **도커 볼륨 (Docker Volume)**: Docker 엔진이 자체 통제하는 스토리지로 볼륨을 생성해 DB나 로그를 완전히 독립적으로 보호합니다.

**[볼륨 영속성 검증 로그]**
```bash
$ docker volume create mydata
$ docker run -d --name vol-test -v mydata:/data ubuntu sleep infinity
$ docker exec -it vol-test bash -c "echo 'hello volume' > /data/test.txt"
$ docker rm -f vol-test
$ docker run -d --name vol-test2 -v mydata:/data ubuntu sleep infinity
$ docker exec -it vol-test2 cat /data/test.txt
hello volume
```
*(결과 검증: 첫 컨테이너를 완벽히 파괴했음에도 불구하고, 동일 볼륨 경로를 마운트한 새 컨테이너에서 test.txt 파일이 보존됨을 확인)*

작업 완료 후, 시스템 리소스 낭비를 막기 위해 미사용 이미지와 구동을 멈춘 목록의 깔끔한 클리어 조치를 수행했습니다.
```bash
$ docker ps -a
$ docker rmi hello-world
Untagged: hello-world:latest
Deleted: sha256:eb84fdc6f2a3a...
```

---

## 5. 변경 이력 제어 및 원격 저장소 배포 (Git & GitHub)

기초적인 전역 유저 정보를 세팅하고, 구현된 인프라 산출물을 1차 커밋하여 GitHub 워크스페이스 상에 안정적으로 동기화(Push) 완료했습니다.
```bash
$ git config --global user.name "jeonghyeon"
$ git config --global user.email "new.codey99@gmail.com"
$ git init
$ git add . && git commit -m "docs: init"
$ git remote add origin https://github.com/newcode99/Codyssey.git
$ git push -u origin main
```
![Git 브랜치 동기화 확인](./01/images/git-branch.png)  
*(VSCode 환경에서 로컬 main과 원격 origin/main 의 완벽한 트래킹 연동 확인)*

---

## 6. 심층 회고 및 트러블슈팅 (Troubleshooting)

### Trouble 1. 호스트 포트 충돌에 따른 매핑 실패 진단 시나리오
컨테이너 배포 시 `port is already allocated` 와 같은 에러 조우 시의 대응 매뉴얼입니다.
1. 먼저 `lsof -i :8080` 이나 `netstat -ano` 를 타격하여 호스트 측에서 해당 포트를 점유하고 있는 프로세스를 색출합니다.
2. `docker ps -a` 명령어로 본인도 모르게 시스템 백그라운드에서 살아 숨 쉬는 방치된 컨테이너가 포트를 물고 있는지 찾아냅니다.
3. 원흉 프로세스를 강제 `kill` 시키거나, 운영체제 필수망일 경우 `-p 8081:80` 처럼 타겟 우회 매핑을 실시하여 충돌을 안전하게 돌파합니다.

### Trouble 2. 컨테이너 잔여 쓰레기에 의한 네임스페이스 이름 충돌 극복
*   **가설 설정**: 볼륨 컨테이너 할당 중 `The container name is already in use` 충돌 발생. 멈춰둔 컨테이너가 동작만 멈춘(Exited) 것일 뿐, 시스템 Namespace 상에는 존재 좌표가 그대로 남아있을 것이라 추론.
*   **증명 및 조치**: `docker ps` 대신 보이지 않는 시체까지 띄워주는 `-a` 필터로 구동이 중단된 과거 컨테이너 흔적을 포착. 즉각 `docker rm -f vol-test` 로 찌꺼기를 날려버린 후 재구동하자 성공함. 컨테이너 라이프 사이클의 엄격한 폐기 절차를 인지한 중요한 회고 포인트였습니다.

### Trouble 3. 무기명 접근 차단(No anonymous write access) 권한 에러 해결
*   GitHub로 Push 진행 시 권한 인가가 거절됨.
*   정책상의 SSH 키 또는 패스워드 토큰 인증이 누락되었음을 인지하고, VSCode 내부의 Source Control Auth 플로우를 통해 Oauth 권한 승인을 돌파해 안전하게 원격지 코드를 전송 마감했습니다.
