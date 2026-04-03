# AI/SW 개발 워크스테이션 구축 기술 문서 및 과제 평가 답변서

본 문서는 과제 평가 항목 18건에 대한 서술형 답변 및 기능 동작 증빙 로그를 모두 포함한 최종 기술 문서(답안지)입니다.

---

## 1. 기능 동작 검증 (실습 증빙)

### Q1. 터미널에서 기본 명령어로 폴더/파일 생성·이동·삭제를 수행한 흔적이 있는가?
**[수행 내역 및 로그]**
*   명령어 `pwd`, `ls`, `mkdir` 등을 활용하여 프로젝트 기초를 세팅했습니다.
```bash
$ pwd
/Users/hwangjeonghyeon/practice/python-practice
$ mkdir test
$ ls -la
01    test
```

### Q2. 파일 권한 변경 결과가 확인되는가?
**[수행 내역 및 로그]**
*   `chmod` 명령어로 `test` 디렉토리의 접근 제어를 조작하여 소유자의 실행(접근)권한 박탈을 검증했습니다.
```bash
$ chmod 644 test
$ ls -ld test
drw-r--r--  2 hwangjeonghyeon  staff  64 Apr  2 23:06 test
# 변경 결과: rwx (7) 이었던 디렉토리가 644(rw-r--r--)로 변경되어, cd 명령어를 통한 디렉토리 내부 엑세스가 불가해짐을 확인.
```

### Q3. docker --version이 출력되고, Docker가 동작 가능한 상태인가?
**[수행 내역 및 로그]**
*   로컬 Mac 환경에서 OrbStack 데몬을 가동한 뒤 Docker 엔진 연결 상태를 검증했습니다.
```bash
$ docker --version
Docker version 28.5.2, build ecc6942
$ docker info
Server Version: 28.5.2 \ Operating System: OrbStack \ CPUs: 8 \ Total Memory: 7.808GiB
```

### Q4. docker run hello-world가 정상 실행되는가?
**[수행 내역 및 로그]**
*   Docker Hub에서 공식 이미지를 Pull받아 컨테이너 생명주기가 정상 작동함을 확인했습니다.
```bash
$ docker run hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

### Q5. 이미지/컨테이너 목록 확인 및 정리 흔적이 있는가?
**[수행 내역 및 로그]**
*   사용한 테스트 컨테이너와 불필요한 이미지를 강제 삭제(`-f`)하여 스토리지를 정리했습니다.
```bash
$ docker ps -a
$ docker rm -f vol-test
$ docker rmi hello-world
Untagged: hello-world:latest
Deleted: sha256:eb84fdc6f2a3a...
```

### Q6. Dockerfile로 이미지 빌드가 가능한가?
**[수행 내역 및 로그]**
*   `nginx:alpine`을 베이스 이미지로 사용하는 Dockerfile을 작성 후 빌드했습니다.
```dockerfile
# 01/Dockerfile
FROM nginx:alpine
LABEL maintainer="hwangjeonghyeon"
COPY app/ /usr/share/nginx/html/
EXPOSE 80
```
```bash
$ docker build -t my-web:1.0 .
```

### Q7. 매핑된 포트로 접속이 가능한가?
**[수행 내역 및 로그]**
*   로컬 호스트의 8080포트와 컨테이너의 80포트를 매핑(`-p 8080:80`)하여 브라우저로 접근했습니다.
```bash
$ docker run -d -p 8080:80 --name my-web-8080 my-web:1.0
```
![포트 매핑 증명 완료](./01/images/port-map.png)

### Q8. Docker 볼륨 데이터가 컨테이너 삭제 후에도 유지되는가?
**[수행 내역 및 로그]**
*   Docker Managed Volume(`mydata`)을 생성하고 컨테이너를 파괴(`rm -f`)하더라도 데이터가 영구 보존됨을 확인했습니다.
```bash
$ docker volume create mydata
$ docker run -d --name vol-test -v mydata:/data ubuntu sleep infinity
$ docker exec -it vol-test bash -c "echo 'hello volume' > /data/test.txt"
$ docker rm -f vol-test
$ docker run -d --name vol-test2 -v mydata:/data ubuntu sleep infinity
$ docker exec -it vol-test2 cat /data/test.txt
hello volume
# 결과: 새 컨테이너(vol-test2)에서 이전 컨테이너의 파일(test.txt)이 그대로 유지됨 검증 성공.
```

### Q9. Git 설정 및 GitHub 연동이 확인되는가?
**[수행 내역 및 로그]**
*   사용자 전역 설정 후, 로컬 워크스페이스를 GitHub 원격 저장소(`Codyssey.git`)에 Push 하였습니다.
```bash
$ git config --global user.name "jeonghyeon"
$ git config --global user.email "new.codey99@gmail.com"
$ git init
$ git add . && git commit -m "docs: init"
$ git remote add origin https://github.com/newcode99/Codyssey.git
$ git push -u origin main
```
![Git 브랜치 동기화 확인](./01/images/git-branch.png)  

---

## 2. 동작 구조 설계 (아키텍처)

### Q10. 프로젝트 디렉토리 구조를 어떤 기준으로 구성했는지 설명할 수 있는가?
*   **설계 기준**: "환경의 격리와 역할의 분리"를 기준으로 폴더 트리를 설계했습니다. 웹 서버가 노출시킬 정적 자산(Static Assets)은 `./01/app/` 폴더 내부에 격리하여 보안을 높이고, 이를 조립하는 설계도인 `Dockerfile`과 문서인 `README.md`는 프로젝트 최상위 로컬 루트 디렉토리에 배치하여 형상 관리(Git)와 유지 보수를 용이하게 하였습니다. 문서에 쓰이는 이미지 에셋 역시 `images` 폴더를 별도로 빼어 관리했습니다.

### Q11. 포트/볼륨 설정을 어떤 방식으로 재현 가능하게 정리했는지 설명할 수 있는가?
*   **재현성 확보 방식**: 제 코드를 클론 받은 누구라도 인프라를 재현할 수 있도록 CLI 명령어를 정형화했습니다. 
*   포트 설정: `docker run -p 8080:80`을 통해 Host:Container 규격을 명시하였고, 
*   볼륨 설정: `docker run -v $(pwd)/01/app:/usr/share/nginx/html` 처럼 바인드 마운트에 `$(pwd)` 환경변수를 삽입하여, 사용하는 OS나 타 사용자의 사용자명이 다르더라도 자동으로 현재 절대경로를 추적하여 무조건 동일한 위치가 마운트되도록 재현성을 극대화했습니다.

---

## 3. 핵심 기술 원리 적용 (서술 개념)

### Q12. 이미지와 컨테이너의 차이를 '빌드/실행/변경' 관점에서 구분해 설명할 수 있는가?
*   **빌드(Build) 관점**: 이미지는 OS, 라이브러리, 코드가 층층이 쌓인 읽기 전용(Read-Only)의 '불변 템플릿(설계도)'입니다. 
*   **실행(Run) 관점**: 컨테이너는 이 이미지를 기반으로 메모리에 올라가 살아 숨 쉬는 '실행 중인 프로세스 인스턴스(건물)'입니다.
*   **변경 관점**: 컨테이너 안에서 파일을 새로 만들거나 수정하더라도(쓰기 가능 레이어), 이는 원본 이미지에 절대 반영되지 않습니다. 컨테이너가 파괴되면 수정 내용도 소멸하며, 이미지를 변경하려면 Dockerfile을 고쳐 완전히 새 이미지로 다시 '빌드'해야 합니다.

### Q13. 컨테이너 내부 포트로 직접 접속할 수 없는 이유와 필요한 이유를 설명할 수 있는가?
*   **직접 접속이 불가한 이유(격리)**: 컨테이너는 커널의 Network Namespace를 사용하여 호스트 머신(내 맥북)과는 완전히 격리된 별도의 가상 사설 IP 대역망을 구성하기 때문입니다.
*   **포트 매핑이 필요한 이유**: 외부 브라우저(통신망)에서 컨테이너 내부로 패킷을 뚫고 들어가려면, 호스트의 특정 포트(예: 8080)로 통신이 왔을 때 포워딩(NAT)을 통해 내부 컨테이너 포트(80)로 길을 열어주는 교통정리(포트 매핑)가 필수적이기 때문입니다.

### Q14. 절대 경로/상대 경로를 어떤 상황에서 선택하는지 설명할 수 있는가?
*   **상대 경로 선택 (`./app`)**: 현재 자신이 위치한 작업 디렉토리를 기준으로 이동할 때 사용합니다. 코드 내부의 모듈을 참조하거나, 터미널에서 가까운 이웃 폴더로 빠르게 이동할 때 유리합니다.
*   **절대 경로 선택 (`/Users/hwang/..`)**: 루트(`/`)부터 시작하는 불변의 고정 주소입니다. 시스템 환경 설정 파일 제어나, **Docker -v 옵션을 통한 바인드 마운트** 시 무조건 절대경로를 적용해야만 경로 이탈 없이 안전하고 정확하게 호스트의 타겟을 컨테이너 안에 연결할 수 있습니다.

### Q15. 파일 권한 숫자 표기가 어떤 규칙으로 결정되는지 설명할 수 있는가?
*   Linux의 권한은 8진수 숫자로 소유자/그룹/기타 3그룹을 제어합니다.
*   규칙은 2진수 합산체계로 **4(r:읽기), 2(w:쓰기), 1(x:실행)**을 의미합니다.
*   예를 들어 권한이 `644`라면, 첫 자리수 6은 소유자(4+2=rw-), 두 번째 자리수 4는 그룹(4=r--), 세 번째 4는 기타사용자(4=r--)가 되어 타인의 파일 무단 훼손을 강력하게 방지합니다.

---

## 4. 심층 인터뷰 (트러블슈팅 및 회고)

### Q16. '호스트 포트가 이미 사용 중'이라 매핑이 실패한다면, 어떤 순서로 원인을 진단할지 설명할 수 있는가?
*   **진단 시나리오**: `Bind for 0.0.0.0:8080 failed: port is already allocated` 알람 조우.
    1.  먼저 `lsof -i :8080` (Mac/Linux) 또는 `netstat -ano` 를 입력하여 호스트 상에서 8080 포트를 점유하고 있는 PID(프로세스 이름)의 정체를 파악합니다.
    2.  `docker ps -a`를 쳐서, 나도 모르게 이전에 실행시켜 둔 채로 방치한 백그라운드 구동 컨테이너가 8080을 물고 있는지 점검합니다.
    3.  원인 파악 후, 해당 프로세스나 컨테이너를 강제 종료(`kill` 또는 `docker rm -f`)하거나, 부득이한 경우 Docker 실행 명령(`-p 8081:80`)을 통해 타겟 포트만 우회하여 충돌을 회피하는 조치를 취할 것입니다.

### Q17. 컨테이너 삭제 후 데이터가 사라진 경험이 있다면, 이를 방지하기 위한 대안을 설명할 수 있는가?
*   데이터 유실을 막으려면 데이터 보관소를 컨테이너의 생명주기와 완벽하게 분리해야 합니다. 대안은 2가지입니다.
*   **대안 1 (Docker Volume)**: Docker 엔진이 자체적으로 관리하여 가장 안전하고 이식성이 높은 Volume(`docker run -v mydata:/data`)을 사용하여 반영구적인 DB, 로그 정보를 보관합니다.
*   **대안 2 (Bind Mount)**: 코드를 짜면서 지속적으로 즉각 동기화가 필요하다면 호스트의 특정 절대 경로 파일시스템 자체를 컨테이너에 거울처럼 직결시키는 Bind Mount(`-v $(pwd)/app:/app`)를 채택하여 즉각 핫리로드(Hot-reload)를 담보합니다.

### Q18. 가장 어려웠던 지점과 해결 과정(가설 → 확인 → 조치)
*   **문제 발생**: Docker 볼륨 실습 시, `docker run -d --name vol-test` 커맨드를 쳤을 때 `Conflict` 이름 충돌 에러가 발생하여 더 이상 진척되지 않았습니다.
*   **가설 수립**: "분명히 `docker stop`으로 아까 멈춰뒀는데 왜 이름이 없다고 뜨지? 컨테이너가 작동을 멈추는 것과 시스템 상에서 자리가 삭제되는 것은 다른 개념일 것이다"라는 가설을 세웠습니다.
*   **확인 방식**: `docker ps`(현재 실행 중)를 쳤을 때는 비어있었으나, 숨겨진 찌꺼기까지 보여주는 명령어인 `docker ps -a`를 쳐보니 예전에 멈춘 상태(Exited)로 잠들어있던 `vol-test` 컨테이너 레이어를 발견했습니다.
*   **조치 및 회고**: `docker rm -f vol-test`를 입력하여 시체 컨테이너를 호스트 루트에서 완전히 박살 내어 삭제하였고, 이후 다시 실행하여 정상 구동에 성공했습니다. 컨테이너의 가벼움 이면에 숨겨진 '동작 상태'와 '존재 상태'의 엄격한 생명주기 격리를 깨달은 소중한 지점이었습니다.
