# 와인 챗봇 기능 : 화면과 JSON API (API는 http://localhost:8000/docs 에서 테스트 가능)

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from openai import OpenAIError

from chat.agent_builder import delete_chat_history, get_chat_history, run_agent
from chat.schemas import ChatMessage, ChatRequest, ChatResponse
from common.markdown_utils import render_markdown
from common.templating import templates

logger = logging.getLogger(__name__)

router = APIRouter()

THREAD_COOKIE = "wine_thread_id"


# 브라우저별로 대화를 구분 (이전 프로젝트의 고정 THREAD_ID를 쿠키로 변경)
def get_thread_id(request: Request, response: Response):
    thread_id = request.cookies.get(THREAD_COOKIE)
    if not thread_id:
        thread_id = uuid4().hex
        response.set_cookie(THREAD_COOKIE, thread_id, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30)
    return thread_id


# 소믈리에 챗봇 화면
@router.get("/chat", response_class=HTMLResponse, include_in_schema=False)
def chat_page(request: Request):
    return templates.TemplateResponse(request, "chat/chat.html")


# 챗봇 질문
@router.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat(body: ChatRequest, request: Request, thread_id: str = Depends(get_thread_id)):
    try:
        answer, tools_used = await run_agent(request.app.state.agent, body.message, thread_id)
    except OpenAIError:
        logger.exception("에이전트 실행 실패")
        raise HTTPException(status_code=502, detail="AI 모델 호출에 실패했습니다. 잠시 후 다시 시도해 주세요.")

    answer = answer or "답변을 생성하지 못했습니다. 질문을 바꿔서 다시 시도해 주세요."
    return {"answer": answer, "html": render_markdown(answer), "tools_used": tools_used}


# 저장된 대화 조회 (새로고침해도 대화 유지)
@router.get("/api/chat/history", response_model=list[ChatMessage], tags=["chat"])
async def chat_history(request: Request, thread_id: str = Depends(get_thread_id)):
    history = await get_chat_history(request.app.state.agent, thread_id)
    return [{**message, "html": render_markdown(message["content"])} for message in history]


# 저장된 대화 삭제 (새 대화)
@router.delete("/api/chat/history", status_code=204, tags=["chat"])
async def clear_chat_history(request: Request, thread_id: str = Depends(get_thread_id)):
    await delete_chat_history(request.app.state.agent, thread_id)
