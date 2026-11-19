# 와인 챗봇 API 요청/응답 스키마

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    html: str
    tools_used: list[str]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    html: str
