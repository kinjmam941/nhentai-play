from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="nhentai-play", version="1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routes
from app.routes import home, search, hentai, genres, episodes
app.include_router(home.router)
app.include_router(search.router)
app.include_router(hentai.router)
app.include_router(genres.router)
app.include_router(episodes.router)

@app.on_event("startup")
async def startup():
    from app.utils.client import hhaven_client
    await hhaven_client.build()
