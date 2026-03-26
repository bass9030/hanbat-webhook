import os
from dotenv import load_dotenv

load_dotenv()

# Discord 웹훅 설정
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')

# 크롤링 설정
TARGET_URL = 'https://www.hanbat.ac.kr/prog/bbsArticle/BBSMSTR_000000000323/list.do'
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 기본값 5분

# 저장소 설정
POSTS_DB_FILE = 'posts.json'
LOG_FILE = 'crawler.log'
