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
    """마지막으로 확인한 게시글 번호 관리"""

    def __init__(self, db_file=POSTS_DB_FILE):
        self.db_file = db_file
        self.last_post_no = self._load_last_post_no()

    def _load_last_post_no(self):
        """저장된 마지막 게시글 번호 로드 (없거나 구버전 형식이면 None)"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return int(data['last_post_no'])
            except Exception as e:
                logger.error(f"게시글 번호 로드 실패: {e}")
        return None

    def save_last_post_no(self, post_no):
        """마지막 게시글 번호 저장"""
        self.last_post_no = post_no
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump({'last_post_no': post_no}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"게시글 번호 저장 실패: {e}")


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
            req_body = {
                "pageIndex": 1,
                "cmsNoStr": "",
                "nttId": "",
                "mno": "sub05_01",
                "searchCondition": "all",
                "searchKeyword": "",
                "pageUnit": 10
            }
            response = self.session.post(TARGET_URL, data=req_body, timeout=10)
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
            rows = table.select('tr:not(.notice)')  # 공지사항 제외
            
            for row in reversed(rows):
                # notice 클래스 제외
                # if 'notice' in row.get('class', []):
                #     continue
                
                try:
                    cols = row.find_all('td')
                    if len(cols) < 3:
                        continue
                    
                    # 제목과 링크 추출
                    title_elem = cols[1].find('a')
                    if not title_elem:
                        continue

                    # 게시글 번호 (정수가 아니면 일반 게시글이 아니므로 제외)
                    post_no = cols[0].get_text(strip=True)
                    if not post_no.isdigit():
                        continue
                    post_no = int(post_no)

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
                        'post_no': post_no,
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
        if not all_posts:
            return []

        # 최초 실행(저장된 번호 없음): 알림 없이 현재 최신 번호를 기준으로 저장
        if self.db.last_post_no is None:
            self.db.save_last_post_no(max(p['post_no'] for _, p in all_posts))
            logger.info(f"기준 게시글 번호 저장: {self.db.last_post_no}")
            return []

        new_posts = []
        for post_id, post_data in all_posts:
            if post_data['post_no'] > self.db.last_post_no:
                new_posts.append((post_id, post_data))
                logger.info(f"신규 게시글 감지: {post_data['title']}")

        if new_posts:
            new_posts.sort(key=lambda x: x[1]['post_no'])
            self.db.save_last_post_no(new_posts[-1][1]['post_no'])

        return new_posts
    
    def close(self):
        """세션 종료"""
        self.session.close()
