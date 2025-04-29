from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
from app.utils.client import client, initialize_client

app = FastAPI(title="nHentai Play", version="1.0.0")

# Configuration
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.add_middleware(GZipMiddleware)

# Import routes after client initialization
from app.routes import home, search, hentai, genres
app.include_router(home.router)
app.include_router(search.router)
app.include_router(hentai.router)
app.include_router(genres.router)

@app.on_event("startup")
async def on_startup():
    await initialize_client()
    app.state.client = client
