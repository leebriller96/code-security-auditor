#!/usr/bin/env python3
# build_report.py — Markdown 보안 레포트를 HTML과 PDF로 변환한다.
# 사용법: python3 tools/build_report.py reports/2606291651_security_report.md
# 결과: 같은 디렉토리에 동일 이름의 .html, .pdf 파일 생성.
#
# 의존성:
#   필수: markdown  (pip install markdown)
#   PDF : weasyprint (pip install weasyprint)  ← 미설치 시 HTML만 생성하고 안내.

import sys
import os
import datetime

# 심각도별 색상 (HTML 배지/스타일에 사용)
SEVERITY_COLORS = {
    "Critical": "#b00020",
    "High": "#e65100",
    "Medium": "#f9a825",
    "Low": "#2e7d32",
    "Info": "#1565c0",
}

# HTML 문서 골격 + 스타일. 가독성 있는 레포트 출력을 위해 CSS를 내장한다.
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Noto Sans KR", sans-serif;
         line-height: 1.65; color: #1a1a1a; max-width: 900px; margin: 0 auto; padding: 40px 24px; }}
  h1 {{ border-bottom: 3px solid #1a1a1a; padding-bottom: 8px; }}
  h2 {{ margin-top: 2.2em; border-bottom: 1px solid #ddd; padding-bottom: 6px; }}
  h3 {{ margin-top: 1.6em; }}
  code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-size: 0.92em; }}
  pre {{ background: #f7f7f7; border: 1px solid #e0e0e0; border-radius: 6px;
        padding: 14px; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
  th {{ background: #f0f0f0; }}
  blockquote {{ border-left: 4px solid #ccc; margin: 1em 0; padding: 4px 16px; color: #555; }}
  .footer {{ margin-top: 3em; padding-top: 1em; border-top: 1px solid #ddd;
            color: #888; font-size: 0.85em; }}
  /* 심각도 텍스트 강조 */
  {severity_css}
</style>
</head>
<body>
{content}
<div class="footer">생성: {generated} · code-security-auditor</div>
</body>
</html>
"""


def build_severity_css() -> str:
    # "Critical" 등 심각도 단어를 색상으로 강조하는 CSS 클래스 생성
    rules = []
    for name, color in SEVERITY_COLORS.items():
        rules.append(f".sev-{name.lower()} {{ color: {color}; font-weight: 700; }}")
    return "\n  ".join(rules)


def md_to_html(md_text: str, title: str) -> str:
    try:
        import markdown  # 지연 임포트로 미설치 시 친절한 에러 제공
    except ImportError:
        sys.exit("[build_report] 'markdown' 패키지가 필요합니다. 설치: pip install markdown")

    # 표/코드펜스/목차 등 확장 기능 활성화
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )
    generated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return HTML_TEMPLATE.format(
        title=title,
        content=body,
        severity_css=build_severity_css(),
        generated=generated,
    )


def html_to_pdf(html_text: str, pdf_path: str) -> bool:
    # weasyprint가 있으면 PDF 생성, 없으면 False 반환
    try:
        from weasyprint import HTML  # 지연 임포트
    except Exception:
        return False
    try:
        HTML(string=html_text).write_pdf(pdf_path)
        return True
    except Exception as exc:  # 시스템 라이브러리(cairo/pango) 누락 등
        print(f"[build_report] PDF 생성 실패: {exc}")
        return False


def main():
    if len(sys.argv) < 2:
        sys.exit("사용법: python3 tools/build_report.py <레포트.md>")

    md_path = sys.argv[1]
    if not os.path.isfile(md_path):
        sys.exit(f"[build_report] 파일을 찾을 수 없습니다: {md_path}")

    base, _ = os.path.splitext(md_path)
    html_path = base + ".html"
    pdf_path = base + ".pdf"

    with open(md_path, encoding="utf-8") as f:
        md_text = f.read()

    title = os.path.basename(base)
    html_text = md_to_html(md_text, title)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_text)
    print(f"[build_report] HTML 생성: {html_path}")

    if html_to_pdf(html_text, pdf_path):
        print(f"[build_report] PDF 생성: {pdf_path}")
    else:
        print("[build_report] PDF는 생성하지 못했습니다. "
              "weasyprint 설치 필요: pip install weasyprint "
              "(시스템 라이브러리 cairo/pango도 필요)")


if __name__ == "__main__":
    main()
