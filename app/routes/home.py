from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.utils.client import client

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    homepage = await client.home()
    genres = await client.get_all_genres()  # Fixed genre loading
    
    return request.app.state.templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "trending": homepage.trending_month,
            "latest": homepage.last,
            "genres": genres[:8]  # Show first 8 genres
        }
    )
