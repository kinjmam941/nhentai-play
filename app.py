from flask import Flask, render_template_string, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import re

app = Flask(__name__)

# Cache configuration
CACHE_DURATION = 300  # 5 minutes
cache = {
    'homepage': {'data': None, 'timestamp': 0},
    'search': {}
}

def get_cached_data(key, query=None):
    current_time = time.time()
    if query:
        if key in cache and query in cache[key] and current_time - cache[key][query]['timestamp'] < CACHE_DURATION:
            return cache[key][query]['data']
    else:
        if key in cache and current_time - cache[key]['timestamp'] < CACHE_DURATION:
            return cache[key]['data']
    return None

def set_cached_data(key, data, query=None):
    current_time = time.time()
    if query:
        if key not in cache:
            cache[key] = {}
        cache[key][query] = {'data': data, 'timestamp': current_time}
    else:
        cache[key] = {'data': data, 'timestamp': current_time}

def fetch_videos(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://hanime.tv/'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        videos = []
        video_cards = soup.find_all('div', class_='video-card-row')
        
        for card in video_cards:
            try:
                title = card.find('h3', class_='video-title').text.strip()
                link = 'https://hanime.tv' + card.find('a', href=True)['href']
                
                # Extract thumbnail (handle different formats)
                thumbnail_div = card.find('div', class_='video-card-image')
                thumbnail = thumbnail_div.find('img')['src'] if thumbnail_div.find('img') else None
                if thumbnail and thumbnail.startswith('//'):
                    thumbnail = 'https:' + thumbnail
                
                # Extract views and duration
                metadata = card.find('div', class_='video-card-meta').text.strip()
                views = re.search(r'(\d+\.?\d*[KM]?) views', metadata)
                views = views.group(1) if views else 'N/A'
                
                duration = re.search(r'(\d+:\d+)', metadata)
                duration = duration.group(1) if duration else 'N/A'
                
                videos.append({
                    'title': title,
                    'link': link,
                    'thumbnail': thumbnail,
                    'views': views,
                    'duration': duration
                })
            except Exception as e:
                print(f"Error parsing video card: {e}")
                continue
        
        return videos
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

@app.route('/')
def index():
    cached_videos = get_cached_data('homepage')
    if cached_videos:
        videos = cached_videos
    else:
        url = "https://hanime.tv/browse"
        videos = fetch_videos(url)
        if videos is not None:
            set_cached_data('homepage', videos)
    
    return render_template_string(HTML_TEMPLATE, 
                               videos=videos if videos else [],
                               search_results=False,
                               query='',
                               error=None if videos else "Failed to fetch videos. Please try again later.")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('index'))
        return redirect(url_for('search_results', q=query))
    
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    cached_results = get_cached_data('search', query)
    if cached_results:
        videos = cached_results
    else:
        url = f"https://hanime.tv/search?query={quote_plus(query)}"
        videos = fetch_videos(url)
        if videos is not None:
            set_cached_data('search', videos, query)
    
    return render_template_string(HTML_TEMPLATE, 
                                videos=videos if videos else [],
                                search_results=True,
                                query=query,
                                error=None if videos else "Failed to fetch search results. Please try again later.")

# ... (Keep the same HTML_TEMPLATE, ABOUT_PAGE, and ERROR_TEMPLATE as before) ...
# HTML Templates
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if search_results %}Search: {{ query }} | {% endif %}HStream Browser</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #6c5ce7;
            --secondary: #a29bfe;
            --dark: #2d3436;
            --light: #f5f6fa;
            --danger: #d63031;
            --success: #00b894;
            --warning: #fdcb6e;
            --info: #0984e3;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f8f9fa;
            color: var(--dark);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo i {
            color: var(--warning);
        }
        
        nav ul {
            display: flex;
            list-style: none;
            gap: 20px;
        }
        
        nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            padding: 5px 10px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        nav a:hover, nav a.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .search-container {
            margin: 2rem 0;
        }
        
        .search-form {
            display: flex;
            max-width: 600px;
            margin: 0 auto;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            border-radius: 50px;
            overflow: hidden;
        }
        
        .search-input {
            flex: 1;
            padding: 12px 20px;
            border: none;
            font-size: 1rem;
            outline: none;
        }
        
        .search-btn {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 0 25px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .search-btn:hover {
            background-color: var(--secondary);
        }
        
        .page-title {
            text-align: center;
            margin: 2rem 0;
            color: var(--dark);
        }
        
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
            margin: 2rem 0;
        }
        
        .video-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .video-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        }
        
        .video-thumbnail {
            position: relative;
            height: 160px;
            overflow: hidden;
        }
        
        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        
        .video-card:hover .video-thumbnail img {
            transform: scale(1.05);
        }
        
        .video-duration {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .video-info {
            padding: 15px;
        }
        
        .video-title {
            font-weight: 600;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            height: 3em;
        }
        
        .video-views {
            color: #666;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .video-views i {
            color: var(--primary);
        }
        
        .error-message {
            text-align: center;
            padding: 2rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            color: var(--danger);
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
        }
        
        .empty-state i {
            font-size: 3rem;
            color: var(--secondary);
            margin-bottom: 1rem;
        }
        
        footer {
            background-color: var(--dark);
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .footer-content {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        .social-links a {
            color: white;
            font-size: 1.2rem;
            transition: color 0.3s ease;
        }
        
        .social-links a:hover {
            color: var(--secondary);
        }
        
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 15px;
            }
            
            nav ul {
                gap: 10px;
            }
            
            .video-grid {
                grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <div class="logo">
                <i class="fas fa-play-circle"></i>
                <span>HStream Browser</span>
            </div>
            <nav>
                <ul>
                    <li><a href="{{ url_for('index') }}" {% if not search_results %}class="active"{% endif %}>Home</a></li>
                    <li><a href="{{ url_for('about') }}">About</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main class="container">
        <div class="search-container">
            <form class="search-form" action="{{ url_for('search') }}" method="POST">
                <input type="text" class="search-input" name="query" placeholder="Search videos..." value="{{ query }}" required>
                <button type="submit" class="search-btn"><i class="fas fa-search"></i></button>
            </form>
        </div>
        
        <h1 class="page-title">
            {% if search_results %}
                Search Results for "{{ query }}"
            {% else %}
                Trending Videos
            {% endif %}
        </h1>
        
        {% if error %}
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>{{ error }}</p>
            </div>
        {% elif not videos %}
            <div class="empty-state">
                <i class="fas fa-video-slash"></i>
                <h3>No videos found</h3>
                <p>{% if search_results %}Try a different search term{% else %}Failed to load videos{% endif %}</p>
            </div>
        {% else %}
            <div class="video-grid">
                {% for video in videos %}
                    <a href="{{ video.link }}" class="video-card" target="_blank">
                        <div class="video-thumbnail">
                            {% if video.thumbnail %}
                                <img src="{{ video.thumbnail }}" alt="{{ video.title }}">
                            {% else %}
                                <img src="https://via.placeholder.com/280x160?text=No+Thumbnail" alt="No thumbnail">
                            {% endif %}
                            <span class="video-duration">{{ video.duration }}</span>
                        </div>
                        <div class="video-info">
                            <h3 class="video-title">{{ video.title }}</h3>
                            <div class="video-views">
                                <i class="fas fa-eye"></i>
                                <span>{{ video.views }}</span>
                            </div>
                        </div>
                    </a>
                {% endfor %}
            </div>
        {% endif %}
    </main>
    
    <footer>
        <div class="container footer-content">
            <div class="social-links">
                <a href="#"><i class="fab fa-github"></i></a>
                <a href="#"><i class="fab fa-twitter"></i></a>
                <a href="#"><i class="fab fa-discord"></i></a>
            </div>
            <p>&copy; 2023 HStream Browser. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About | HStream Browser</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Same styles as in HTML_TEMPLATE */
        :root {
            --primary: #6c5ce7;
            --secondary: #a29bfe;
            --dark: #2d3436;
            --light: #f5f6fa;
            --danger: #d63031;
            --success: #00b894;
            --warning: #fdcb6e;
            --info: #0984e3;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f8f9fa;
            color: var(--dark);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo i {
            color: var(--warning);
        }
        
        nav ul {
            display: flex;
            list-style: none;
            gap: 20px;
        }
        
        nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            padding: 5px 10px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        nav a:hover, nav a.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .about-section {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        
        .about-section h1 {
            color: var(--primary);
            margin-bottom: 1.5rem;
        }
        
        .about-section p {
            margin-bottom: 1rem;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 2rem 0;
        }
        
        .feature-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        
        .feature-card i {
            font-size: 2rem;
            color: var(--primary);
            margin-bottom: 1rem;
        }
        
        footer {
            background-color: var(--dark);
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .footer-content {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        .social-links a {
            color: white;
            font-size: 1.2rem;
            transition: color 0.3s ease;
        }
        
        .social-links a:hover {
            color: var(--secondary);
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <div class="logo">
                <i class="fas fa-play-circle"></i>
                <span>HStream Browser</span>
            </div>
            <nav>
                <ul>
                    <li><a href="{{ url_for('index') }}">Home</a></li>
                    <li><a href="{{ url_for('about') }}" class="active">About</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main class="container">
        <div class="about-section">
            <h1>About HStream Browser</h1>
            <p>HStream Browser is an advanced web application that allows you to browse and search videos from HStream.moe with a modern and user-friendly interface.</p>
            <p>This application was built using Python with Flask for the backend, and modern HTML/CSS for the frontend. It features responsive design, caching for better performance, and an intuitive user interface.</p>
            
            <h2 style="margin-top: 2rem; color: var(--primary);">Features</h2>
            <div class="features">
                <div class="feature-card">
                    <i class="fas fa-bolt"></i>
                    <h3>Fast Performance</h3>
                    <p>Built with caching mechanisms to ensure quick loading times and reduce server requests.</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-mobile-alt"></i>
                    <h3>Responsive Design</h3>
                    <p>Works perfectly on all devices from desktop computers to mobile phones.</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-search"></i>
                    <h3>Advanced Search</h3>
                    <p>Powerful search functionality to help you find exactly what you're looking for.</p>
                </div>
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container footer-content">
            <div class="social-links">
                <a href="#"><i class="fab fa-github"></i></a>
                <a href="#"><i class="fab fa-twitter"></i></a>
                <a href="#"><i class="fab fa-discord"></i></a>
            </div>
            <p>&copy; 2023 HStream Browser. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error {{ error_code }} | HStream Browser</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Same styles as in HTML_TEMPLATE */
        :root {
            --primary: #6c5ce7;
            --secondary: #a29bfe;
            --dark: #2d3436;
            --light: #f5f6fa;
            --danger: #d63031;
            --success: #00b894;
            --warning: #fdcb6e;
            --info: #0984e3;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f8f9fa;
            color: var(--dark);
            line-height: 1.6;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo i {
            color: var(--warning);
        }
        
        .error-container {
            text-align: center;
            padding: 3rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
        }
        
        .error-icon {
            font-size: 5rem;
            color: var(--danger);
            margin-bottom: 1.5rem;
        }
        
        .error-container h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: var(--dark);
        }
        
        .error-container p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            color: #666;
        }
        
        .home-btn {
            display: inline-block;
            background-color: var(--primary);
            color: white;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .home-btn:hover {
            background-color: var(--secondary);
            transform: translateY(-2px);
        }
        
        footer {
            background-color: var(--dark);
            color: white;
            text-align: center;
            padding: 2rem 0;
        }
        
        .footer-content {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        .social-links a {
            color: white;
            font-size: 1.2rem;
            transition: color 0.3s ease;
        }
        
        .social-links a:hover {
            color: var(--secondary);
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <div class="logo">
                <i class="fas fa-play-circle"></i>
                <span>HStream Browser</span>
            </div>
            <nav>
                <ul>
                    <li><a href="{{ url_for('index') }}">Home</a></li>
                    <li><a href="{{ url_for('about') }}">About</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main class="container">
        <div class="error-container">
            <div class="error-icon">
                {% if error_code == 404 %}
                    <i class="fas fa-exclamation-circle"></i>
                {% else %}
                    <i class="fas fa-times-circle"></i>
                {% endif %}
            </div>
            <h1>Error {{ error_code }}</h1>
            <p>{{ error_message }}</p>
            <a href="{{ url_for('index') }}" class="home-btn">Return to Homepage</a>
        </div>
    </main>
    
    <footer>
        <div class="container footer-content">
            <div class="social-links">
                <a href="#"><i class="fab fa-github"></i></a>
                <a href="#"><i class="fab fa-twitter"></i></a>
                <a href="#"><i class="fab fa-discord"></i></a>
            </div>
            <p>&copy; 2023 HStream Browser. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
