# 과제 진행
  ├── 🖥️  터미널 (Linux CLI)
  │     ├── 작업 디렉토리 이동 및 파일 조작
  │     └── 파일 권한 설정
  │
  ├── 🐳 Docker
  │     ├── OrbStack으로 Docker 환경 구성
  │     ├── 기본 명령어 (images, ps, logs, stats)
  │     ├── Dockerfile → 커스텀 이미지 빌드
  │     ├── 포트 매핑으로 웹 서버 접속
  │     └── 바인드 마운트 / 볼륨 영속성 검증
  │
  └── 🔀 Git & GitHub
        ├── Git 설정 (사용자 정보, 브랜치)
        └── GitHub 연동 + VSCode 연동



# AI/SW 개발 워크스테이션 구축 기술 문서

터미널, Docker, Git 세 도구를 직접 세팅하고 검증한 과정 기록.
단순히 명령어를 실행하는 것이 아닌 각 도구가 어떤 문제를 해결하는지,
왜 이런 구조로 설계됐는지를 이해하고 실무 환경 기준으로 재현 가능한 개발 환경을 구축한다.

## 1. 실행 환경
*   **OS**: macOS (Apple Silicon)
*   **Shell**: /bin/zsh
*   **Git**: git version 2.39.5 (Apple Git-154)
*   **Docker**: Docker version 28.5.2 (OrbStack 환경 기반)

## 2. 과제 수행 체크리스트
- [x] 터미널 권한/파일 조작 및 목록/현재위치 확인 로그 기록
- [x] 권한 변경 실습 (디렉토리 rwx 변경)
- [x] Docker 설치/점검 (`docker info`, `docker --version`) 결과 기록
- [x] 기본 컨테이너 런칭 및 `hello-world`, `ubuntu` 내부 진입 실행 로그
- [x] Dockerfile 커스텀 이미지 (Nginx 베이스) 빌드 증거
- [x] 포트 매핑 (8080:80) 및 바인드 마운트 (8081:80) 실행 검증 (스크린샷 포함)
- [x] Docker 볼륨 영속성 (`mydata`) 증명 완료
- [x] Git 사용자 설정 및 GitHub 원격 저장소 연동 및 Push 완료 (연동 스크린샷 포함)
- [x] 트러블슈팅 2건 이상 작성 완료

---

## 3. 터미널 조작 로그 및 권한 실습 (파트 A)

**1) 현재 위치 확인 및 폴더/파일 목록 확인**
```bash
$ pwd
/Users/hwangjeonghyeon/practice/python-practice

$ ls -la
01    pa.md
```

**2) 터미널 권한 변경 결과 분석 실습**
(`test` 폴더 생성 및 chmod 권한 실험 조작)
```bash
$ mkdir test
$ chmod 644 test
$ ls -ld test
drw-r--r--  2 hwangjeonghyeon  staff  64 Apr  2 23:06 test
# 분석: 644(-rw-r--r--) 적용 시, 소유자도 디렉토리에 x(실행, cd 등 접근) 권한이 박탈됨을 확인. 테스트 후 안전하게 삭제함.
```

---

## 4. Docker 운영 및 인프라 구축 로그 (파트 B)

**1) Docker 설치 및 데몬(Daemon) 점검**
```bash
$ docker --version
Docker version 28.5.2, build ecc6942

$ docker info
Server Version: 28.5.2
Operating System: OrbStack
CPUs: 8
Total Memory: 7.808GiB
Docker Root Dir: /var/lib/docker
```

**2) 첫 컨테이너 구동 테스트 및 Linux OS 진입 확인**
```bash
$ docker run hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.

# Ubuntu 컨테이너 껍데기를 깨고 내부로 진입하여 격리된 Linux 파일 시스템 확인
$ docker run -it ubuntu bash
root@b45314c54282:/# cat /etc/os-release
PRETTY_NAME="Ubuntu 22.04.4 LTS"
```

**3) 커스텀 Dockerfile 빌드 및 포트 매핑 접속 증거**
*(`nginx:alpine` 베이스 이미지를 빌드하여 8080 및 8081 포트에 매핑)*
```bash
$ docker build -t my-web:1.0 .

$ docker run -d -p 8080:80 --name my-web-8080 my-web:1.0
c44537b45cd129372960259f883056004a4db7160b78f337939e0b3e21be5f53
```
![포트매핑 증거](./01/images/port-map.png)  
*(▲ 8080 포트를 통해 호스트 환경에서 컨테이너 웹 서버에 정상 접근한 증거)*

**4) 바인드 마운트 실시간 소스 반영 증거**
```bash
$ docker run -d -p 8081:80 --name my-web-mount -v $(pwd)/app:/usr/share/nginx/html my-web:1.0
```

![바인드마운트 증거](./01/images/bind-mount.png)  
*(▲ 이미지를 재빌드하지 않고도 볼륨 공유를 통해 호스트 터미널에서 수정한 index.html 코드가 브라우저에 즉시 반영됨)*

**5) Docker 볼륨 영속성 검증 (핵심 증거 자료)**
*(볼륨을 연결해 데이터를 넣고, 컨테이너를 파괴한 뒤 새 컨테이너를 띄워 파일 보존 여부 증명)*
```bash
$ docker volume create mydata
$ docker run -d --name vol-test -v mydata:/data ubuntu sleep infinity

$ docker exec -it vol-test bash -c "echo 'hello from vol-test' > /data/hello.txt && cat /data/hello.txt"
hello from vol-test

$ docker rm -f vol-test
vol-test

$ docker run -d --name vol-test2 -v mydata:/data ubuntu sleep infinity
6da740b1d3583c457e08453f18c1f26fe344d65c2b35198387126a67287f02fa

$ docker exec -it vol-test2 bash -c "cat /data/hello.txt"
hello from vol-test
# 증명: 컨테이너(vol-test)가 완전히 삭제되었음에도 mydata 볼륨을 통해 hello.txt 내용이 영구 보존됨.
```

---

## 5. Git 환경 구축 및 원격 저장소 연동 로그 (파트 C)

**1) Git 전역 설정 로그 확인** (닉네임, 이메일, 기본 브랜치 검증)
```bash
$ git config --list
credential.helper=osxkeychain
init.defaultbranch=main
user.name=jeonghyeon
user.email=new.codey99@gmail.com
```

**2) 원격(Remote) 저장소 동기화 및 Push 완료 증거**
```bash
$ git init
$ git commit -m "workspace"

$ git remote add origin https://github.com/newcode99/Codyssey.git
$ git push -u origin main
```
![Git 브랜치 동기화 확인](./01/images/git-branch.png)  
*(▲ VSCode 환경에서 로컬의 main 브랜치와 원격 origin/main 브랜치가 성공적으로 트래킹 연동된 상태 확인)*

---

## 6. 트러블슈팅 (문제 해결 이력)

### Case 1: Docker 볼륨 컨테이너 이름 중복 충돌 (Conflict)
*   **문제 현상**: 볼륨 테스트를 하기 위해 `docker run -d --name vol-test...`를 쳤으나 `Conflict. The container name "/vol-test" is already in use by container "28ce38b97e...".` 에러 발생.
*   **원인 파악**: Docker 데몬 아키텍처 상, 네임스페이스 영역에서 동일한 컨테이너 이름(`vol-test`)을 소유한 레이어가 중복 구동될 수 없음. 이전에 띄운 인스턴스가 죽었더라도 완전히 삭제된 상태가 아니었기에 충돌함.
*   **해결 및 검증**: `docker rm -f vol-test` 커맨드로 중지된 프로세스 레이어를 강제 걷어낸 후 재구동하여 문제 해결.

### Case 2: Git Push 인증 실패 (익명 권한 차단)
*   **문제 가설**: GitHub로 저장소를 밀어 올릴 때 `remote: No anonymous write access. fatal: Authentication failed` 에러 발생.
*   **원인 파악**: GitHub의 보안 강화 정책으로 인해 원격 저장소에 Push할 때 무기명 접근(단순 PWD)이 원천 차단됨. Mac의 Credential Helper와 터미널 간에 정상적인 인증 세션이 확립되어 있지 않은 상태였음.
*   **해결 및 검증**: 터미널과 브라우저 기반 Auth Flow(Oauth/Device Login)를 혼용하여 본인 인증 트리거를 수락하거나 VSCode의 자체 GitHub 권한 증명(Source Control Auth)을 활용해 계정을 인가시킴. 이후 `branch 'main' set up` 응답과 함께 강제 연결을 마침.
