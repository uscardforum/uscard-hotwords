import requests
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime, timedelta
import re
import os

API_URL = 'https://www.uscardforum.com/latest.json'
KEYWORDS_OUTPUT_PATH = 'output/index.html'
STOPWORDS = {'the', 'a', 'is', 'are', 'to', 'for', 'in', 'of', 'on', 'and', 'with', 'this', 'that'}

def fetch_titles_last_24_hours():
    r = requests.get(API_URL)
    data = r.json()
    posts = data.get('topic_list', {}).get('topics', [])
    titles = []
    now = datetime.utcnow()

    for post in posts:
        created = datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if now - created <= timedelta(days=1):
            titles.append(post['title'])
    
    return titles

def extract_keywords(titles):
    words = []
    for title in titles:
        title = re.sub(r'[^a-zA-Z0-9 ]', '', title.lower())
        words.extend(title.split())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return Counter(words).most_common(50)

def generate_html(top_keywords):
    html = "<html><head><meta charset='utf-8'><title>Hot Words</title></head><body>"
    html += "<h1>🔥 过去 24 小时 USCard 热词排行榜</h1><ul>"
    for word, count in top_keywords:
        html += f"<li>{word} ({count})</li>"
    html += "</ul><p>最后更新: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC") + "</p>"
    html += "</body></html>"

    os.makedirs('docs', exist_ok=True)
    with open(KEYWORDS_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    titles = fetch_titles_last_24_hours()
    keywords = extract_keywords(titles)
    generate_html(keywords)
