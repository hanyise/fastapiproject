# 🍷 AI 와인 소믈리에 (FastAPI)

FastAPI + Jinja2로 화면과 API를 함께 제공하는 와인 추천 서비스입니다.
와인 데이터를 ChromaDB에 임베딩해 유사도 검색을 하고, LangChain 에이전트 기반 챗봇이 와인을 추천합니다.

## 주요 기능

- **와인 검색** : 벡터 유사도 검색 (유사도 점수 표시)
- **가격/재고 필터** : 메타데이터 필터로 조건을 정확히 적용
- **AI 소믈리에 챗봇** : 대화 기록 유지 (브라우저 쿠키별 구분)
- **YouTube 영상 추천** : 사용자가 요청할 때 와인 관련 영상 검색

## 기술 스택

| 구분 | 사용 기술 |
|------|-----------|
| 웹 서버/화면 | FastAPI, Uvicorn, Jinja2, CSS, JavaScript |
| 벡터 검색 | ChromaDB, OpenAI `text-embedding-3-small` (코사인 거리) |
| AI 에이전트 | LangChain, LangGraph, OpenAI `gpt-5-nano` |
| 대화 기록 | SQLite (langgraph-checkpoint-sqlite) |

## 프로젝트 구조

```
fastapiproject/
├─ requirements.txt
└─ backend/                  # 실행 위치
   ├─ main.py                # FastAPI 앱, 라우터 연결
   ├─ common/                # 설정, 템플릿, 마크다운 변환
   ├─ home/                  # 홈 화면
   ├─ search/                # 검색 화면/API, 가격·재고 필터
   ├─ chat/                  # 챗봇 화면/API, 에이전트, 도구(search_wine, youtube_search)
   ├─ vectordb/              # 임베딩 생성(create_vector_db.py), ChromaDB 검색
   ├─ templates/             # Jinja2 화면 (base, home, search, chat)
   ├─ static/                # style.css, chat.js
   ├─ data/                  # wine_brief.csv, wine_detail.md (와인 60종)
   └─ storage/               # 실행 시 자동 생성 (ChromaDB, 대화 기록 DB)
```

## 실행 방법

1. 프로젝트 루트에 `.env` 파일을 만들고 OpenAI API 키를 설정합니다.

   ```
   OPENAI_API_KEY=sk-...
   ```

2. 가상환경 생성 및 라이브러리 설치

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 벡터 DB 생성 (최초 1회, 데이터 변경 시 재실행) 후 서버 실행

   ```powershell
   cd backend
   python vectordb/create_vector_db.py
   uvicorn main:app --reload
   ```

4. 브라우저에서 http://localhost:8000 접속

## URL 목록

| Method | URL | 설명 |
|--------|-----|------|
| GET | `/` | 홈 |
| GET | `/search` | 와인 검색 화면 |
| GET | `/chat` | 와인 챗봇 화면 |
| GET | `/api/search` | 유사도 검색 (JSON) |
| POST | `/api/chat` | 챗봇 질문 `{"message": "..."}` |
| GET | `/api/chat/history` | 저장된 대화 조회 |
| DELETE | `/api/chat/history` | 저장된 대화 삭제 |

`/api/search` 파라미터 : `query`, `source_type`(all \| Structured Data \| Unstructured Data), `k`(1~10), `min_price`·`max_price`(만원), `in_stock_only`

```
/api/search?query=불고기&max_price=20&in_stock_only=true
```

API 문서는 http://localhost:8000/docs 에서 확인할 수 있습니다.

## 주의사항

- `create_vector_db.py`를 다시 실행했다면 **서버를 재시작**해야 새 벡터로 검색됩니다.
- 지역 필터와 "가장 저렴한 와인" 같은 정렬 검색은 지원하지 않습니다.
- 임베딩, 검색, 챗봇 사용 시 OpenAI API 비용이 발생합니다.
- `.env`와 `backend/storage/`는 git에 올리지 않습니다.
