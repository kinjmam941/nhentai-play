from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.utils.client import hhaven_client

router = APIRouter()

@router.get("/hentai/{hentai_id}", response_class=HTMLResponse)
async def hentai_detail(request: Request, hentai_id: int):
    try:
        hentai = await hhaven_client.get_hentai(hentai_id)
        return request.app.state.templates.TemplateResponse("hentai.html", {
            "request": request,
            "hentai": hentai,
            "episodes": hentai.episodes
        })
    except Exception as e:
        raise HTTPException(status_code=404, detail="Hentai not found")
