from flask import Flask, render_template_string, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time

app = Flask(__name__)

# Updated headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://hstream.moe/'
}

def fetch_videos(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Updated selectors - inspect the current site structure
        video_items = soup.find_all('div', class_='video-item') or soup.find_all('div', class_='video-card')  # Try common class names
        
        videos = []
        for item in video_items:
            try:
                title = item.find('a', class_='video-title') or item.find('h3')
                link = title['href'] if title and title.get('href') else None
                views = item.find('span', class_='views') or item.find('span', class_='view-count')
                thumbnail = item.find('img')['src'] if item.find('img') else None
                duration = item.find('span', class_='duration') or item.find('span', class_='time')
                
                if not title or not link:
                    continue
                    
                videos.append({
                    'title': title.get_text().strip(),
                    'link': link if link.startswith('http') else f'https://hstream.moe{link}',
                    'views': views.get_text().strip() if views else 'N/A',
                    'thumbnail': thumbnail,
                    'duration': duration.get_text().strip() if duration else 'N/A'
                })
            except Exception as e:
                print(f"Error parsing video item: {e}")
                continue
        return videos
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

@app.route('/')
def index():
    url = "https://hstream.moe/"
    videos = fetch_videos(url)
    return render_template_string(HTML_TEMPLATE, 
                               videos=videos if videos else [],
                               search_results=False,
                               query='',
                               error=None if videos else "Failed to fetch videos. The site structure may have changed or we're being blocked.")

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query', '') if request.method == 'POST' else request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    url = f"https://hstream.moe/search?q={quote_plus(query)}"
    videos = fetch_videos(url)
    return render_template_string(HTML_TEMPLATE, 
                                videos=videos if videos else [],
                                search_results=True,
                                query=query,
                                error=None if videos else "No results found or we're being blocked.")

# ... (keep the rest of your existing code - HTML_TEMPLATE, etc.)

if __name__ == '__main__':
    app.run(debug=True)
