import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import logging
from config import TARGET_URL, POSTS_DB_FILE, LOG_FILE

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

class PostsDatabase:
    """게시글 데이터베이스 관리"""
    
    def __init__(self, db_file=POSTS_DB_FILE):
        self.db_file = db_file
        self.posts = self._load_posts()
    
    def _load_posts(self):
        """저장된 게시글 로드"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"게시글 로드 실패: {e}")
                return []
        return []
    
    def save_posts(self):
        """게시글 저장"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.posts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"게시글 저장 실패: {e}")
    
    def add_post(self, post_id):
        """새 게시글 추가"""
        self.posts.append(post_id)
        
        if len(self.posts) > 10:
            self.posts = self.posts[-10:]

        self.save_posts()
    
    def has_post(self, post_id):
        """게시글 존재 여부 확인"""
        return post_id in self.posts
    
    def get_all_posts(self):
        """모든 게시글 반환"""
        return self.posts


class Crawler:
    """한밭대학교 공지사항 크롤러"""
    
    def __init__(self):
        self.db = PostsDatabase()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self):
        """페이지 가져오기"""
        try:
            response = self.session.get(TARGET_URL, timeout=10)
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            logger.error(f"페이지 로드 실패: {e}")
            return None
    
    def parse_posts(self, html_content):
        """게시글 파싱"""
        if not html_content:
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            posts = []
            
            # 게시글 테이블 찾기
            table = soup.find('table', {'class': 'board_list'})
            if not table:
                table = soup.find('table')
            
            if not table:
                logger.warning("게시글 테이블을 찾을 수 없습니다")
                return []
            
            # 행(tr) 찾기
            rows = table.find_all('tr')
            
            for row in reversed(rows[1:]):  # 머리글 제외
                # notice 클래스 제외
                if 'notice' in row.get('class', []):
                    continue
                
                try:
                    cols = row.find_all('td')
                    if len(cols) < 3:
                        continue
                    
                    # 제목과 링크 추출
                    title_elem = cols[1].find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)

                    # 게시글 ID는 링크에서 추출 (URL 전체를 ID로 사용)
                    post_id = title_elem.get('onclick', '')
                    post_id = post_id.split("('")[1].split("')")[0]

                    link = 'https://www.hanbat.ac.kr/prog/bbsArticle/BBSMSTR_000000000323/view.do?nttId=' + post_id
                    
                    # 작성자
                    author = cols[2].get_text(strip=True) if len(cols) > 2 else '알 수 없음'
                    
                    # 조회수
                    views = cols[3].get_text(strip=True) if len(cols) > 4 else '0'

                    # 작성일
                    date = cols[4].get_text(strip=True) if len(cols) > 3 else ''
                    
                    post = {
                        'title': title,
                        'link': link,
                        'author': author,
                        'date': date,
                        'views': views
                    }
                    
                    posts.append((post_id, post))
                
                except Exception as e:
                    logger.debug(f"행 파싱 중 오류: {e}")
                    continue
            
            return posts
        
        except Exception as e:
            logger.error(f"HTML 파싱 중 오류: {e}")
            return []
    
    def get_new_posts(self):
        """신규 게시글 가져오기"""
        html = self.fetch_page()
        if not html:
            return []
        
        all_posts = self.parse_posts(html)
        new_posts = []
        
        for post_id, post_data in all_posts:
            if not self.db.has_post(post_id):
                new_posts.append((post_id, post_data))
                self.db.add_post(post_id)
                logger.info(f"신규 게시글 감지: {post_data['title']}")
        
        return new_posts
    
    def close(self):
        """세션 종료"""
        self.session.close()
