from flask import Flask, render_template_string, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus

app = Flask(__name__)

def get_driver():
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_videos(url):
    try:
        driver = get_driver()
        driver.get(url)
        time.sleep(3)  # wait for JavaScript to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        videos = []
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
    except Exception as e:
        print(f"Driver error: {e}")
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

# simple HTML template
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
