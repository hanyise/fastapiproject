# 와인 검색 기능 : 화면과 JSON API (API는 http://localhost:8000/docs 에서 테스트 가능)

import logging

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from openai import OpenAIError

from common.templating import templates
from search.schemas import PriceQuery, SearchResponse, SourceType
from vectordb.wine_store import get_chunk_counts, search_wines

logger = logging.getLogger(__name__)

router = APIRouter()


# 와인 검색 화면 : /search?query=...&source_type=all&k=5&min_price=&max_price=20&in_stock_only=true
@router.get("/search", response_class=HTMLResponse, include_in_schema=False)
def search_page(
    request: Request,
    query: str = Query("", max_length=500),
    source_type: SourceType = "all",
    k: int = Query(5, ge=1, le=10),
    min_price: PriceQuery = None,
    max_price: PriceQuery = None,
    in_stock_only: bool = False
):
    query = query.strip()
    results = []
    error = None

    if query:
        if min_price is not None and max_price is not None and min_price > max_price:
            error = "최소 가격이 최대 가격보다 큽니다. 가격 범위를 다시 입력해 주세요."
        elif get_chunk_counts()["total"] == 0:
            error = "벡터 DB가 비어 있습니다. backend 폴더에서 python vectordb/create_vector_db.py 를 먼저 실행해 주세요."
        else:
            try:
                results = search_wines(query, source_type, k, min_price, max_price, in_stock_only)
            except OpenAIError:
                error = "임베딩 모델 호출에 실패했습니다. API 키와 네트워크 상태를 확인해 주세요."

    return templates.TemplateResponse(request, "search/search.html", {
        "query": query,
        "source_type": source_type,
        "k": k,
        "min_price": min_price,
        "max_price": max_price,
        "in_stock_only": in_stock_only,
        "results": results,
        "error": error
    })


# 유사도 검색 API
@router.get("/api/search", response_model=SearchResponse, tags=["search"])
def search(
    query: str = Query(min_length=1, max_length=500),
    source_type: SourceType = "all",
    k: int = Query(5, ge=1, le=10),
    min_price: PriceQuery = None,
    max_price: PriceQuery = None,
    in_stock_only: bool = False
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="최소 가격이 최대 가격보다 큽니다.")

    if get_chunk_counts()["total"] == 0:
        raise HTTPException(status_code=503, detail="벡터 DB가 비어 있습니다. python vectordb/create_vector_db.py 를 먼저 실행해 주세요.")

    try:
        results = search_wines(query, source_type, k, min_price, max_price, in_stock_only)
    except OpenAIError:
        logger.exception("임베딩 모델 호출 실패")
        raise HTTPException(status_code=502, detail="임베딩 모델 호출에 실패했습니다.")

    return {
        "query": query,
        "source_type": source_type,
        "k": k,
        "min_price": min_price,
        "max_price": max_price,
        "in_stock_only": in_stock_only,
        "results": results
    }
