from flask import Flask, render_template_string, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

app = Flask(__name__)

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
        
        videos = []
        
        # Adapt this based on real inspection
        for item in soup.select('div.film-poster'):
            try:
                link_tag = item.find('a', href=True)
                img_tag = item.find('img')
                
                if not link_tag or not img_tag:
                    continue
                
                title = img_tag.get('alt', 'No Title').strip()
                link = link_tag['href']
                thumbnail = img_tag.get('data-src') or img_tag.get('src')
                
                videos.append({
                    'title': title,
                    'link': link if link.startswith('http') else f'https://hstream.moe{link}',
                    'thumbnail': thumbnail,
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
                                  error=None if videos else "Failed to fetch videos.")

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query', '') if request.method == 'POST' else request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    url = f"https://hstream.moe/filter?keyword={quote_plus(query)}"
    videos = fetch_videos(url)
    return render_template_string(HTML_TEMPLATE,
                                  videos=videos if videos else [],
                                  search_results=True,
                                  query=query,
                                  error=None if videos else "No results found.")

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HStream Scraper</title>
</head>
<body>
    <h1>{% if search_results %}Search Results for "{{ query }}"{% else %}Latest Videos{% endif %}</h1>
    
    <form method="post" action="{{ url_for('search') }}">
        <input type="text" name="query" placeholder="Search..." required>
        <input type="submit" value="Search">
    </form>
    
    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}
    
    <div style="display:flex;flex-wrap:wrap;">
        {% for video in videos %}
            <div style="margin:10px;">
                <a href="{{ video.link }}" target="_blank">
                    <img src="{{ video.thumbnail }}" alt="{{ video.title }}" style="width:150px;height:auto;"><br>
                    {{ video.title }}
                </a>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
