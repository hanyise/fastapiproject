# 마크다운을 HTML로 변환

from markdown_it import MarkdownIt

# js-default : 원본 HTML 태그를 이스케이프하고 javascript: 링크를 차단하므로
#              LLM 답변을 화면에 그대로 출력해도 스크립트가 실행되지 않음
_markdown = MarkdownIt("js-default", {"linkify": True})


def render_markdown(text):
    return _markdown.render(text)
