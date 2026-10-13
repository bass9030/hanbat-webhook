# Hanbat-webhook

한밭대학교 공지사항 페이지에서 신규 게시글을 자동으로 감지하고 Discord 웹훅으로 전송하는 자동화 도구입니다.

## 기능

- 한밭대 신규 게시글 자동 감지
- ✅ Discord 웹훅으로 실시간 알림
- ✅ 주기적 자동 확인 (기본값: 5분)
- ✅ 게시글 번호 기반 신규 게시글 감지 (중복 알림 방지)
- ✅ 상세 로깅

## 설치

### 필수 요구사항

- [uv](https://docs.astral.sh/uv/)
- Python 3.10 이상

### 1. 의존성 설치

```bash
uv sync
```

### 2. 설정 파일 생성

`.env.example`을 참고하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

또는 직접 생성:

```env
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
CHECK_INTERVAL=300
```

## 사용 방법

### 명령줄 실행

```bash
uv run main.py
```

### Docker를 통한 실행

본 프로젝트는 docker및 docker-compose를 통한 실행을 지원합니다.

docker-compse:

```yaml
services:
    hanbat-rss:
        image: hanbat-rss
        build: ./
        volumes:
            - ./posts.json:/usr/src/app/posts.json
        environment:
            - TZ=Asia/Seoul
        env_file:
            - .env
        restart: unless-stopped
```

이후 `docker-compose up -d`등을 통해 실행

docker:

```bash
docker run -d \
  --name hanbat-rss \
  -v ./posts.json:/usr/src/app/posts.json \
  --env-file .env \
  hanbat-rss
```

## 설정 옵션

### `config.py`

| 설정                  | 설명                                  |
| --------------------- | ------------------------------------- |
| `DISCORD_WEBHOOK_URL` | Discord 웹훅 URL (필수)               |
| `TARGET_URL`          | 크롤링 대상 URL                       |
| `CHECK_INTERVAL`      | 확인 간격 (초, 기본값: 300)           |
| `POSTS_DB_FILE`       | 마지막 게시글 번호 저장 파일 (기본값: posts.json) |
| `LOG_FILE`            | 로그 파일 (기본값: crawler.log)       |

## 라이선스

MIT License
