#!/bin/bash
# Wolfram Alpha Full Results API helper
# Использование: wolfram.sh v1 "<input>" | v2 "<input>"
# AppID читается из env-файла (WOLFRAM_APPID).
set -u
ENVF="${WOLFRAM_ENV:-${GEOTECH_ENV:-$HOME/.openclaw/.env}}"
APPID=$(grep "^WOLFRAM_APPID=" "$ENVF" | cut -d= -f2)
[ -n "$APPID" ] || { echo "WOLFRAM_APPID не найден в $ENVF"; exit 2; }
MODE="${1:-v2}"; INPUT="${2:?нужен input}"
if [ "$MODE" = "v1" ]; then
  curl -s -G --max-time 40 "https://api.wolframalpha.com/v1/result" \
    --data-urlencode "appid=$APPID" --data-urlencode "i=$INPUT"
else
  curl -s -G --max-time 40 "https://api.wolframalpha.com/v2/query" \
    --data-urlencode "appid=$APPID" --data-urlencode "output=JSON" \
    --data-urlencode "input=$INPUT"
fi
