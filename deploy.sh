#!/bin/bash
set -euo pipefail

cd ~/GAM

echo "[1/4] Git pull..."
git reset --hard HEAD
git pull origin live-server

REQ_FILE="requirements.txt"
HASH_FILE=".requirements.sha256"

echo "[2/4] Check requirements.txt change..."
NEW_HASH=$(sha256sum "$REQ_FILE" | awk '{print $1}')
OLD_HASH=$(cat "$HASH_FILE" 2>/dev/null || echo "")

if [ "$NEW_HASH" != "$OLD_HASH" ]; then
  echo "requirements.txt changed. Installing packages..."
  pip install -r "$REQ_FILE"
  echo "$NEW_HASH" > "$HASH_FILE"
else
  echo "requirements.txt unchanged. Skip pip install."
fi

PORT=9000

echo "[3/4] Stop existing server on port $PORT (with autoreload)..."

# 포트를 점유한 PID들(대개 리로더 자식이 잡힘)
PIDS=$(lsof -t -i :"$PORT" 2>/dev/null || true)

if [ -n "${PIDS}" ]; then
  echo "Found PIDs on port $PORT: ${PIDS}"

  # 포트 PID들이 속한 "세션 리더/프로세스 그룹"을 잡아 한 번에 종료
  # - runserver를 nohup으로 띄우면 보통 같은 세션/그룹으로 묶입니다.
  PGIDS=$(for pid in $PIDS; do
            ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' '
          done | sort -u)

  echo "Killing process groups: ${PGIDS}"
  for pgid in $PGIDS; do
    kill -TERM -- "-$pgid" 2>/dev/null || true
  done

  # 정상 종료 대기(최대 8초)
  for _ in {1..16}; do
    sleep 0.5
    if ! lsof -t -i :"$PORT" >/dev/null 2>&1; then
      break
    fi
  done

  # 여전히 살아있으면 강제 종료
  if lsof -t -i :"$PORT" >/dev/null 2>&1; then
    echo "Still running. Force killing..."
    for pgid in $PGIDS; do
      kill -KILL -- "-$pgid" 2>/dev/null || true
    done
  fi
else
  echo "No process is using port $PORT."
fi

# 포트 비었는지 최종 확인
if lsof -t -i :"$PORT" >/dev/null 2>&1; then
  echo "ERROR: Port $PORT is still in use. Abort."
  exit 1
fi

echo "[4/4] Start Django server..."

nohup python -u manage.py runserver 0.0.0.0:"$PORT" > "./logs/$(date +'%Y%m%d_%H%M%S').log" 2>&1 &

echo "Update Backend complete."
