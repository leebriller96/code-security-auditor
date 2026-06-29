#!/usr/bin/env bash
# run_sast.sh — 대상 경로의 언어를 감지해 적절한 SAST 도구를 실행하고 결과를 JSON으로 모은다.
# 사용법: tools/run_sast.sh <대상경로>
# 출력: reports/.sast/ 아래에 각 도구별 JSON 결과 파일 생성, 요약을 stdout에 출력.
set -uo pipefail

TARGET="${1:-input}"
OUT_DIR="reports/.sast"
mkdir -p "$OUT_DIR"

echo "[run_sast] 대상: $TARGET"

# 설치된 도구만 실행하도록 존재 여부를 먼저 확인한다.
have() { command -v "$1" >/dev/null 2>&1; }

ran_any=0

# 1) Semgrep — 범용 다언어 보안 룰셋
if have semgrep; then
  echo "[run_sast] Semgrep 실행 중..."
  semgrep --config p/security-audit --config p/owasp-top-ten \
    --json --quiet "$TARGET" > "$OUT_DIR/semgrep.json" 2>/dev/null && ran_any=1 \
    && echo "  -> $OUT_DIR/semgrep.json"
else
  echo "[run_sast] semgrep 미설치 (설치: pip install semgrep)"
fi

# 2) Bandit — 파이썬 전용
if find "$TARGET" -name '*.py' -print -quit 2>/dev/null | grep -q . ; then
  if have bandit; then
    echo "[run_sast] Bandit(Python) 실행 중..."
    bandit -r "$TARGET" -f json -o "$OUT_DIR/bandit.json" -q 2>/dev/null; ran_any=1
    echo "  -> $OUT_DIR/bandit.json"
  else
    echo "[run_sast] bandit 미설치 (설치: pip install bandit)"
  fi
fi

# 3) Gitleaks — 하드코딩된 비밀 탐지 (전 언어)
if have gitleaks; then
  echo "[run_sast] Gitleaks(비밀값) 실행 중..."
  gitleaks detect --no-git --source "$TARGET" \
    --report-format json --report-path "$OUT_DIR/gitleaks.json" 2>/dev/null; ran_any=1
  echo "  -> $OUT_DIR/gitleaks.json"
else
  echo "[run_sast] gitleaks 미설치 (설치: https://github.com/gitleaks/gitleaks)"
fi

# 4) 의존성 취약점 — pip-audit / npm audit
if [ -f "$TARGET/requirements.txt" ] && have pip-audit; then
  echo "[run_sast] pip-audit(의존성) 실행 중..."
  pip-audit -r "$TARGET/requirements.txt" -f json > "$OUT_DIR/pip-audit.json" 2>/dev/null; ran_any=1
  echo "  -> $OUT_DIR/pip-audit.json"
fi
if [ -f "$TARGET/package.json" ] && have npm; then
  echo "[run_sast] npm audit(의존성) 실행 중..."
  (cd "$TARGET" && npm audit --json 2>/dev/null) > "$OUT_DIR/npm-audit.json"; ran_any=1
  echo "  -> $OUT_DIR/npm-audit.json"
fi

if [ "$ran_any" -eq 0 ]; then
  echo "[run_sast] 실행 가능한 SAST 도구가 없습니다. claude-only 모드로 분석을 진행하세요."
  exit 2
fi

echo "[run_sast] 완료. 결과 디렉토리: $OUT_DIR"
