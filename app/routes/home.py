from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.utils.client import hhaven_client

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = await hhaven_client.home()
    return request.app.state.templates.TemplateResponse("home.html", {
        "request": request,
        "trending": data.trending_month,
        "latest": data.last,
        "genres": data.yuri + data.ecchi + data.uncensored
    })
