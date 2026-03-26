# hanbat-webhook

> [!NOTE]
> 해당 프로젝트의 일부는 AI로 작성되었습니다.

한밭대학교 학과 공지사항을 주기적으로 크롤링하여 신규 게시물을 Discord 웹훅으로 보내는 Python 스크립트

## 🌟 기능 요약

- 한밭대학교 정보통신공학과 공지사항(https://www.hanbat.ac.kr/prog/bbsArticle/BBSMSTR_000000000323/list.do) 자동 조회
- 새로운 게시글 감지 시 Discord 채널로 알림 발송
- 최근 게시물 ID를 로컬 (`posts.json`)에 캐시하여 중복 알림 방지
- `apscheduler`로 일정 간격 체크 (기본 300초)
- 로깅 (`crawler.log`) 및 에러 처리

## 📁 프로젝트 구조

- `main.py`: 스케줄러 실행 진입점
- `crawler.py`: 크롤링 로직 + 게시글 감지 + 로컬 DB 관리
- `discord_webhook.py`: Discord 웹훅 메시지 전송 (임베드 지원)
- `config.py`: 환경설정 (웹훅 URL, 크롤링 URL, 간격, 파일 경로)
- `posts.json`: 감지된 게시글 ID 저장
- `requirements.txt`: 의존 패키지

## ⚙️ 설치 및 실행

1. 레포 클론

```bash
git clone https://github.com/bass9030/hanbat-webhook
cd hanbat-webhook
```

2. 가상환경 생성/활성화

```bash
python -m venv venv
source venv/bin/activate
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. 환경변수 설정

프로젝트 루트에 `.env`를 생성하고 다음을 기재:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/....
CHECK_INTERVAL=300
```

`CHECK_INTERVAL`은 초 단위 주기(기본 300초)입니다.

5. 실행

```bash
python main.py
```

## 🛠️ 설정

- `config.py`에서 기본 `TARGET_URL`과 파일 경로(`POSTS_DB_FILE`, `LOG_FILE`)를 확인/변경할 수 있습니다.
- `CHECK_INTERVAL`을 `.env` 또는 `config.py`에서 변경하면 주기적으로 크롤링 간격 조정 가능.

## ✅ 동작 방식

1. `main.py`에서 `CrawlerScheduler.start()` 호출
2. 즉시 `check_new_posts()` 실행 (초기 한번)
3. `apscheduler`로 반복 실행
4. `Crawler.get_new_posts()`가 `페이지 fetch -> parse -> 새 게시글 탐지` 수행
5. `new_posts`가 있을 때마다 `DiscordWebhook.send_new_posts()` 호출
6. 신규 게시글이 감지되면 `posts.json`에 ID 추가, `crawler.log`에 기록

## 🚀 Docker (선택)

해당 프로젝트는 Docker를 통한 구동이 가능합니다.

도커 이미지 빌드

```bash
docker image build .
```

docker-compose.yaml

```yaml
services:
    hanbat-webhook:
        image: hanbat-webhook
        build: ./
        volumes:
            - ./posts.json:/usr/src/app/posts.json
        environment:
            - TZ=Asia/Seoul
        env_file:
            - .env
        restart: unless-stopped
```
