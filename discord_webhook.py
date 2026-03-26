import requests
import json
import logging
from datetime import datetime
from config import DISCORD_WEBHOOK_URL

logger = logging.getLogger(__name__)


class DiscordWebhook:
    """Discord 웹훅 전송"""
    
    def __init__(self, webhook_url=DISCORD_WEBHOOK_URL):
        self.webhook_url = webhook_url
        if not webhook_url:
            logger.warning("Discord 웹훅 URL이 설정되지 않았습니다")
    
    def send_embed(self, title, description, url, author='', date=''):
        """Embed 형식으로 메시지 전송"""
        if not self.webhook_url:
            logger.error("웹훅 URL이 없어서 전송할 수 없습니다")
            return False
        
        try:
            embed = {
                "title": title,
                "description": description,
                "url": url,
                "color": 3447003,  # 파란색
                "footer": {
                    "text": "한밭대학교 공지사항"
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            if author:
                embed["author"] = {
                    "name": f"작성자: {author}"
                }
            
            if date:
                embed["fields"] = [
                    {
                        "name": "작성일",
                        "value": date,
                        "inline": True
                    }
                ]
            
            payload = {
                "content": "학과 공지사항 등록: " + title + "\n||@everyone||",
                "embeds": [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info(f"Discord 메시지 전송 성공: {title}")
                return True
            else:
                logger.error(f"Discord 전송 실패 (상태 코드: {response.status_code})")
                return False
        
        except Exception as e:
            logger.error(f"Discord 전송 중 오류: {e}")
            return False
    
    def send_new_posts(self, posts):
        """신규 게시글 전송"""
        if not posts:
            return
        
        for post_id, post_data in posts:
            self.send_embed(
                title=post_data['title'],
                description=f"**작성자:** {post_data['author']}\n**조회수:** {post_data['views']}",
                url=post_data['link'],
                author=post_data['author'],
                date=post_data['date']
            )
