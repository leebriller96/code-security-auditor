# code-security-auditor

코드를 투입하면 **보안 취약점을 탐지**하고, **수정 가이드까지 포함한 레포트**(Markdown/HTML)를
자동으로 생성하는 Claude Code repo입니다. (PDF가 필요하면 HTML을 브라우저에서 Ctrl+P로 저장)

방어적 보안(defensive security)을 위한 도구로, 취약점을 찾아 고치는 것을 목표로 합니다.

## 무엇을 하나요

- `input/`에 코드를 넣거나 코드를 붙여넣고 `/scan` 한 번이면 끝
- OWASP Top 10 / CWE Top 25 기반의 체계적 점검
- 정적분석 도구(Semgrep, Bandit 등) + Claude 심층 분석 결합 (모드 선택 가능)
- 발견 항목마다 위치·심각도·공격 시나리오(개념)·수정 코드(Before/After) 제공
- 레포트를 Markdown + HTML로 export (PDF는 HTML에서 브라우저 인쇄로 저장)

## 빠른 시작

### 1. 준비 (Claude Code)

```bash
git clone <이 repo 주소>
cd code-security-auditor
```

이 디렉토리에서 Claude Code를 실행하면 `CLAUDE.md`, 슬래시 명령, 스킬이 자동 인식됩니다.

### 2. 의존성 설치

레포트(HTML) 생성을 위해 `markdown` 패키지가 필요합니다. (클론 후 1회)

```bash
python -m pip install -r tools/requirements.txt   # HTML 레포트 빌더 (markdown)
```

선택적으로 SAST 도구를 설치하면 `hybrid`/`sast-only` 모드를 쓸 수 있습니다.
미설치 시 자동으로 `claude-only` 모드로 폴백됩니다.

```bash
pip install semgrep bandit pip-audit     # SAST 도구 (선택)
# gitleaks 는 https://github.com/gitleaks/gitleaks 참고
```

PDF는 별도 설치 없이, 생성된 HTML을 브라우저에서 열고 **Ctrl+P → "PDF로 저장"** 으로 만듭니다.
(자동 PDF 생성이 꼭 필요하면 weasyprint를 설치하고 빌더에 `--pdf` 옵션을 붙이면 되지만,
윈도우에서는 GTK 런타임 추가 설치가 필요하므로 기본 경로로는 권장하지 않습니다.)

### 3. 분석 실행

```text
# input/ 에 분석할 코드/디렉토리를 넣은 뒤, Claude Code에서:
/scan

# 모드를 지정하려면:
/scan claude-only     # SAST 없이 Claude 분석만
/scan sast-only       # SAST 결과만 빠르게
/scan hybrid          # (기본) 둘 다 결합
```

코드를 채팅에 직접 붙여넣고 `/scan` 해도 됩니다.

### 4. 결과 확인

```
reports/
  2606291651_security_report.md
  2606291651_security_report.html   ← 브라우저로 열고 Ctrl+P로 PDF 저장 가능
```

파일명은 한국시각(KST) 기준 `yymmddhhmm_` 접두어가 붙습니다.

## 분석 모드

| 모드 | 설명 | 추천 상황 |
|------|------|-----------|
| hybrid | SAST + Claude 분석 결합 (기본) | 정확도 우선, 도구 설치 가능 |
| claude-only | Claude 코드 리딩 분석만 | 의존성 설치 불가 환경 |
| sast-only | SAST 결과 정리만 | 빠른 1차 스크리닝 |

## 지원 언어

1급 지원: **Python, JavaScript/TypeScript, Java/Kotlin**
그 외 언어는 범용 분석(Semgrep 범용 룰셋 + Claude 분석)으로 처리합니다.

## 디렉토리 구조

```
code-security-auditor/
├── .claude/
│   ├── commands/scan.md              # /scan 슬래시 명령
│   └── skills/security-audit/SKILL.md # 취약점 분석 방법론
├── tools/
│   ├── run_sast.sh                   # SAST 실행 래퍼
│   ├── build_report.py               # MD → HTML 변환 (PDF는 선택)
│   └── requirements.txt
├── templates/report_template.md      # 레포트 템플릿
├── input/                            # 분석 대상 코드 투입 (git 무시)
├── reports/                          # 생성 레포트 출력 (git 무시)
└── CLAUDE.md                         # 프로젝트 규칙/컨텍스트
```

## 주의사항

- 이 도구는 방어 목적입니다. 완성형 익스플로잇은 생성하지 않으며, 공격 시나리오는 개념 수준으로만 기술합니다.
- 자동 분석은 보조 수단입니다. 중요한 시스템은 전문가 검토와 병행하세요.
- `input/`에 넣은 코드와 생성된 레포트는 기본적으로 git에 커밋되지 않습니다(.gitignore).

## 라이선스

MIT (필요 시 변경)
