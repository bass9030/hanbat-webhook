#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Event
import sys, signal
from crawler import Crawler
from discord_webhook import DiscordWebhook
from config import CHECK_INTERVAL, DISCORD_WEBHOOK_URL, LOG_FILE

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CrawlerScheduler:
    """크롤러 스케줄러"""
    
    def __init__(self):
        self.crawler = Crawler()
        self.webhook = DiscordWebhook(DISCORD_WEBHOOK_URL)
        self.scheduler = BackgroundScheduler()
    
    def check_new_posts(self):
        """신규 게시글 확인 및 전송"""
        logger.info("신규 게시글 확인 중...")
        
        try:
            new_posts = self.crawler.get_new_posts()
            
            if new_posts:
                logger.info(f"{len(new_posts)}개의 신규 게시글을 발견했습니다")
                self.webhook.send_new_posts(new_posts)
            else:
                logger.info("신규 게시글이 없습니다")
        
        except Exception as e:
            logger.error(f"게시글 확인 중 오류: {e}")
    
    def start(self):
        """스케줄러 시작"""
        logger.info(f"크롤러를 시작합니다 (체크 간격: {CHECK_INTERVAL}초)")
        
        if not DISCORD_WEBHOOK_URL:
            logger.warning("⚠️  경고: Discord 웹훅 URL이 설정되지 않았습니다")
            logger.warning("   .env 파일을 설정한 후 다시 실행해주세요")
        
        # 즉시 한 번 실행
        self.check_new_posts()
        
        # 주기적 실행 설정
        self.scheduler.add_job(
            self.check_new_posts,
            'interval',
            seconds=CHECK_INTERVAL,
            id='hanbat_crawler',
            name='한밭대학교 공지사항 크롤러'
        )
        
        self.scheduler.start()
        
        try:
            logger.info("스케줄러가 실행 중입니다. Ctrl+C로 종료할 수 있습니다.")
            self.scheduler.print_jobs()
            
            signal.signal(signal.SIGTERM, lambda s, f: self.stop())

            # 무한 대기
            Event().wait()
        
        except KeyboardInterrupt:
            logger.info("사용자에 의해 종료되었습니다")
            self.stop()
        
        except Exception as e:
            logger.error(f"스케줄러 오류: {e}")
            self.stop()
    
    def stop(self):
        """스케줄러 중지"""
        logger.info("스케줄러 중지중...")
        self.scheduler.shutdown()
        self.crawler.close()
        logger.info("스케줄러가 중지되었습니다")
        sys.exit(0)


if __name__ == '__main__':
    scheduler = CrawlerScheduler()
    scheduler.start()