import requests
import time
import sqlite3

def init_db():
    conn = sqlite3.connect('trickcal_cafe.db') 
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            article_id INTEGER PRIMARY KEY,
            author TEXT,
            title TEXT,
            url TEXT,
            is_collected INTEGER DEFAULT 0  -- 0: 미수집, 1: 완료
        )
    ''')
    conn.commit()
    conn.close()

def save_articles(article_list):
    conn = sqlite3.connect('trickcal_cafe.db')
    cursor = conn.cursor()
    
    for item in article_list:
        # INSERT OR IGNORE를 쓰면 중복된 ID는 알아서 패스합니다.
        cursor.execute('''
            INSERT OR IGNORE INTO articles (article_id, author, title, url)
            VALUES (?, ?, ?, ?)
        ''', (item['id'], item['nickName'], item['title'], item['url']))
        
    conn.commit()
    conn.close()

def collect_article_urls(cafe_id, menu_id, page_limit=3):
    base_api_url = f"https://apis.naver.com/cafe-web/cafe-boardlist-api/v1/cafes/{cafe_id}/menus/{menu_id}/articles"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Referer': f'https://cafe.naver.com/trickcal'
    }
    
    all_articles = []

    for page in range(1, page_limit + 1):
        params = {
            'page': page,
            'pageSize': 50, 
            'sortBy': 'TIME',
            'viewType': 'L'
        }
        
        try:
            response = requests.get(base_api_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('result', {}).get('articleList', [])
            if not articles:
                print(f"더 이상 가져올 글이 없습니다. (Page {page})")
                break
                
            for article in articles:
                article_id = article.get('item').get('articleId')
                article_nickName = article.get('item').get('writerInfo').get('nickName')
                title = article.get('item').get('subject')
                # 실제 접속 가능한 URL 생성
                article_url = f"https://cafe.naver.com/trickcal/{article_id}"
                
                all_articles.append({
                    'id': article_id,
                    'nickName' : article_nickName,
                    'title': title,
                    'url': article_url
                })

            time.sleep(1.5)
            
        except Exception as e:
            print(f"에러 발생 (Page {page}): {e}")
            break
            
    return all_articles

if __name__ == "__main__" :
    init_db()
    cafe_id = "30131231"
    menu_id = "22"
    article_list = collect_article_urls(cafe_id, menu_id, page_limit=1)
    save_articles(article_list)
