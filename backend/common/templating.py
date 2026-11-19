# 화면 템플릿 공통 설정

from fastapi.templating import Jinja2Templates

from common.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")
