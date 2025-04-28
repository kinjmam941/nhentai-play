from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, FileResponse
import requests
import json
import secrets
from dateutil import parser

app = FastAPI()

@app.get('/')
def root(request: Request):
    return {"root": request.url.hostname}

@app.get('/search')
async def search(query: str, page: int):
    res = {
        "search_text": query,
        "tags": [],
        "brands": [],
        "blacklist": [],
        "order_by": [],
        "ordering": [],
        "page": page,
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    x = requests.post("https://search.htv-services.com", headers=headers, json=res)
    rl = x.json()
    text = {
        "response": json.loads(rl['hits']),
        "page": rl['page']
    }
    return text

@app.get('/recent')
async def recent(page: int = 0):
    url = "https://search.htv-services.com"
    res = {
        "search_text": "",
        "tags": [],
        "brands": [],
        "blacklist": [],
        "order_by": "created_at_unix",
        "ordering": "desc",
        "page": page,
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    x = requests.post(url, headers=headers, json=res)
    rl = x.json()
    text = {
        "reposone": json.loads(rl['hits']),
        "page": rl['page']
    }
    return text

@app.get('/trending')
async def trending(time: str = "month", page: int = 0):
    headers = {
        "X-Signature-Version": "web2",
        "X-Signature": secrets.token_hex(32)
    }
    x = requests.get(f"https://hanime.tv/api/v8/browse-trending?time={time}&page={page}", headers=headers)
    rl = x.json()
    text = {
        "reposone": rl["hentai_videos"],
        "time": rl["time"],
        "page": rl["page"]
    }
    return text

@app.get('/details')
async def details(id: str):
    url = f"https://hanime.tv/api/v8/video?id={id}"
    x = requests.get(url)
    rl = x.json()
    created_at = parser.parse(rl["hentai_video"]["created_at"]).strftime("%Y %m %d")
    released_date = parser.parse(rl["hentai_video"]["released_at"]).strftime("%Y %m %d")
    view = "{:,}".format(rl["hentai_video"]["views"])
    tags = rl["hentai_video"]["hentai_tags"]
    text = {
        "query": rl["hentai_video"]["slug"],
        "name": rl["hentai_video"]["name"],
        "poster": rl["hentai_video"]["cover_url"],
        "id": rl["hentai_video"]["id"],
        "description": rl["hentai_video"]["description"],
        "views": view,
        "brand": rl["hentai_video"]["brand"],
        "created_at": created_at,
        "released_date": released_date,
        "is_censored": rl["hentai_video"]["is_censored"],
        "tags": [x["text"] for x in tags]
    }
    return text

@app.get('/link')
async def hentai_video(id: str):
    url = f"https://hanime.tv/api/v8/video?id={id}"
    x = requests.get(url, headers={
        "X-Session-Token": "your-session-token-here",
    })
    rl = x.json()
    text = {
        "data": rl["videos_manifest"]["servers"][0]["streams"]
    }
    return text

@app.get('/play')
async def m3u8(link: str):
    # HTML and CSS code
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Player</title>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #2c3e50;
            }}
            video {{
                max-width: 100%;
                border: 5px solid #ecf0f1;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }}
        </style>
    </head>
    <body>
        <video id="live" autoplay controls>
            <source src="{link}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)
