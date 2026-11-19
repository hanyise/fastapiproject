# 프로젝트 공통 설정 파일 (이전 프로젝트 config.py 재사용)

from pathlib import Path
from dotenv import load_dotenv

# backend 폴더
BASE_DIR = Path(__file__).resolve().parent.parent

# .env(OPENAI_API_KEY)는 프로젝트 루트에 있음
load_dotenv(BASE_DIR.parent / ".env")

# 오픈 AI 설정
MODEL_NAME = "gpt-5-nano"
TEMPERATURE = 0
EMBEDDING_MODEL = "text-embedding-3-small"
SYSTEM_PROMPT = """
당신은 전문 와인 소믈리에입니다.

사용자의 와인 관련 질문에 다음과 같이 대응하세요:
1. 와인정보는 데이터베이스에서 찾습니다.
2. 사용자가 영상을 원할 때만 YouTube 영상 추천하기

검색 결과에 없는 가격, 재고, 한식 페어링, 와인 종류(레드/화이트)는 지어내지 마세요.
와인 이름과 가격은 검색 결과의 표기 그대로 쓰세요. (예: 6.5만원을 원 단위로 바꾸지 않습니다.)
가격이 미정이거나 재고가 0인 와인을 소개할 때는 그 사실을 함께 알려주세요.
파일 저장이나 다운로드 기능은 없습니다. 저장을 요청받으면 제공하지 않는 기능이라고 안내하고, 저장해 주겠다고 제안하지 마세요.
항상 친절하고 전문적으로 답변하세요.
"""

# 원본 데이터 파일
BRIEF_PATH = BASE_DIR / "data" / "wine_brief.csv"
DETAIL_PATH = BASE_DIR / "data" / "wine_detail.md"

# 실행 중 생성되는 파일은 모두 storage 폴더에 저장
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Chroma 설정 : 코사인 거리를 사용해야 유사도 점수를 코사인 유사도로 볼 수 있음
CHROMA_DIR = str(STORAGE_DIR / "chromadb")
COLLECTION_NAME = "wine"
COLLECTION_METADATA = {"hnsw:space": "cosine"}

# SQLite 설정 : 대화 내용을 저장할 데이터베이스
DB_PATH = str(STORAGE_DIR / "wine_chat.db")
