import requests
import time

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

cafe_id = "30131231"
menu_id = "22"
collected_data = collect_article_urls(cafe_id, menu_id, page_limit=1)

for data in collected_data :
    print(data['nickName'], data['title'], data['url'])
