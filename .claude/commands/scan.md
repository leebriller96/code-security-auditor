---
description: input/ 디렉토리 또는 붙여넣은 코드의 보안 취약점을 분석하고 레포트를 생성합니다.
argument-hint: "[hybrid|claude-only|sast-only] (생략 시 hybrid)"
---

# /scan — 보안 취약점 스캔

사용자가 투입한 코드의 보안 취약점을 분석하고, 수정 가이드를 포함한 레포트를 생성하는 명령입니다.

분석 모드: `$ARGUMENTS` (비어 있으면 `hybrid`로 처리)

## 수행 절차

아래 절차를 순서대로 수행하세요. 상세 방법론은 `.claude/skills/security-audit/SKILL.md`를 반드시 먼저 읽고 따릅니다.

### 1단계 — 분석 대상 확보
- `input/` 디렉토리를 확인합니다. 코드가 있으면 그것을 대상으로 합니다.
- `input/`이 비어 있고 사용자가 채팅에 코드를 붙여넣었다면, 그 코드를 대상으로 합니다.
- 둘 다 없으면 사용자에게 "input/에 코드를 넣거나 코드를 붙여넣어 주세요"라고 안내하고 중단합니다.

### 2단계 — 코드베이스 인벤토리
- 대상 파일 목록, 언어 구성, 진입점, 외부 입력 경로(요청 핸들러, 파일/네트워크 I/O 등)를 파악합니다.
- 규모가 크면 위험도 높은 영역(인증, 입력 처리, 쿼리, 역직렬화, 파일 업로드 등)을 우선순위화합니다.

### 3단계 — 분석 실행 (모드별)
- `hybrid` 또는 `sast-only`: `tools/run_sast.sh <대상경로>`를 실행해 SAST 결과(JSON)를 수집합니다.
  도구가 설치돼 있지 않으면 사용자에게 설치 명령을 안내하되, 가능하면 claude-only로 자동 폴백합니다.
- `hybrid` 또는 `claude-only`: SKILL.md의 취약점 체크리스트에 따라 코드를 직접 정독하며 분석합니다.
- `hybrid`: SAST가 놓친 로직 취약점은 Claude 분석으로 보완하고, SAST 오탐(false positive)은 검증해 걸러냅니다.

### 4단계 — 트리아지
- 발견 항목을 심각도(Critical/High/Medium/Low/Info)로 분류합니다. (기준: CLAUDE.md)
- 오탐으로 판단되면 제외하되, 판단 근거를 레포트의 "검토 제외" 섹션에 남깁니다.

### 5단계 — 레포트 생성
- `templates/report_template.md` 구조에 맞춰 Markdown 레포트를 작성합니다.
- 파일명: `reports/<KST타임스탬프>_security_report.md`
  - 타임스탬프는 `TZ=Asia/Seoul date '+%y%m%d%H%M'` 로 생성.
    (윈도우 PowerShell이면 `Get-Date -Format 'yyMMddHHmm'`)
- 작성 후 **반드시** 레포트 빌더를 실행해 HTML을 생성합니다. (HTML이 기본 산출물)
  - 파이썬 실행 명령은 운영체제에 맞게 선택합니다.
    - 윈도우: `python tools/build_report.py <md경로>`
    - macOS/Linux: `python3 tools/build_report.py <md경로>`
  - `markdown` 패키지가 없다는 에러가 나면 `python -m pip install markdown`(윈도우) /
    `python3 -m pip install markdown`(그 외) 로 설치 후 다시 실행합니다.
- **생성 검증**: 빌더 실행 뒤 `reports/`에 같은 이름의 `.html`이 실제로 생겼는지 확인합니다.
  - `.html`이 없으면 빌더 실행이 실패한 것이므로 에러 메시지를 사용자에게 그대로 전달합니다.
- **PDF 안내**: PDF는 자동 생성하지 않습니다. 생성된 HTML을 브라우저에서 열고
  Ctrl+P(Mac은 Cmd+P) → "PDF로 저장"을 사용하도록 안내합니다.
  (PDF 자동 생성이 꼭 필요한 사용자는 weasyprint 설치 후 `--pdf` 옵션을 붙이면 됩니다.)

### 6단계 — 요약 보고
- 채팅에 핵심 요약(총 발견 수, 심각도 분포, Top 3 우선 조치 항목)을 두괄식으로 보고합니다.
- 생성된 레포트 파일 경로(MD/HTML)를 안내하고, PDF는 HTML을 브라우저에서 Ctrl+P로 저장하면 된다고 덧붙입니다.

## 주의
- 악용 가능한 완성형 익스플로잇은 생성하지 않습니다. 공격 시나리오는 개념 수준으로만 기술합니다.
- 모든 출력은 한글로 작성합니다.
