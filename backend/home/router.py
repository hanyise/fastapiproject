# 홈 화면

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from common.templating import templates
from vectordb.wine_store import get_chunk_counts

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    return templates.TemplateResponse(request, "home/index.html", {"counts": get_chunk_counts()})
