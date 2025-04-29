from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from app.utils.client import client

router = APIRouter()

@router.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: str = Query(None),
    page: int = Query(1, ge=1)
):
    results = []
    if q:
        results = await client.search(q)
    
    return request.app.state.templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "results": results,
            "query": q,
            "page": page
        }
    )
