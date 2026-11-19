# agent 구성 및 생성 파일 (이전 프로젝트 agent_builder.py 재사용)
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from common.config import MODEL_NAME, TEMPERATURE, SYSTEM_PROMPT, DB_PATH
from chat.wine_tools import search_wine
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
from langchain_community.tools import YouTubeSearchTool


# 도구 실행 중 오류가 나도 대화가 끊기지 않도록 오류를 도구 결과로 돌려줌
@wrap_tool_call
async def handle_tool_errors(request, handler):
    try:
        return await handler(request)
    except Exception as e:
        return ToolMessage(content=f"도구 실행 오류: {e}",
                           tool_call_id=request.tool_call["id"], status="error")


#1. 에이전트 생성
async def create_wine_agent():
    conn = await aiosqlite.connect(DB_PATH)
    checkpointer = AsyncSqliteSaver(conn)

    model = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)

    # youtube 도구 구해오기
    youtube_tool = YouTubeSearchTool()

    # 모든 도구 합치기
    all_tools = [search_wine, youtube_tool]

    # 에이전트 생성
    agent = create_agent(
        model = model,
        tools = all_tools,
        checkpointer = checkpointer,
        system_prompt = SYSTEM_PROMPT,
        middleware = [handle_tool_errors]   # 도구 실행 중 오류 처리 미들웨어 추가
    )

    return agent


#2. 에이전트 실행 : 최종 답변과 사용한 도구 이름을 반환
async def run_agent(agent, query, thread_id):
    full_response = ""
    tools_used = []
    config = {"configurable":{"thread_id":thread_id}}

    async for chunk in agent.astream(
        {"messages":[{"role": "user", "content": query}]},
        config=config,
        stream_mode="values"
    ):
        if "messages" not in chunk:
            continue

        latest_msg = chunk["messages"][-1]

        if isinstance(latest_msg, AIMessage):
            if latest_msg.tool_calls:
                tools_used += [call["name"] for call in latest_msg.tool_calls]
            elif latest_msg.text:
                full_response = latest_msg.text

    # WAL 파일에 쌓인 대화 내용을 wine_chat.db 본 파일로 반영
    await agent.checkpointer.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    return full_response, list(dict.fromkeys(tools_used))


#3. 저장된 대화 조회 : 사용자 질문과 최종 답변만 반환
async def get_chat_history(agent, thread_id):
    state = await agent.aget_state({"configurable":{"thread_id":thread_id}})

    history = []
    for msg in state.values.get("messages", []):
        if isinstance(msg, HumanMessage):
            history.append({"role": "user", "content": msg.text})
        elif isinstance(msg, AIMessage) and msg.text and not msg.tool_calls:
            history.append({"role": "assistant", "content": msg.text})
    return history


#4. 저장된 대화 삭제
async def delete_chat_history(agent, thread_id):
    await agent.checkpointer.adelete_thread(thread_id)
