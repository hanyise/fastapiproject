from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from chat.agent_builder import create_wine_agent
from chat.router import router as chat_router
from common.config import BASE_DIR
from home.router import router as home_router
from search.router import router as search_router


# 서버 시작 시 에이전트를 한 번만 만들고, 종료 시 대화 DB 연결을 닫음
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = await create_wine_agent()
    yield
    await app.state.agent.checkpointer.conn.close()


app = FastAPI(title="AI 와인 소믈리에", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(home_router)
app.include_router(search_router)
app.include_router(chat_router)
