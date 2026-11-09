#!/usr/bin/env bash
# Установка «Геотехник Сурок» одной командой: окружение, зависимости, проверка.
#
#   ./install.sh                 — ядро (расчёты по СП 22 и СП 24)
#   ./install.sh --with-engines  — плюс движки: 7 методов устойчивости откосов (xslope)
#                                  и проверки подпорных стен (geoeq)
#   ./install.sh --no-verify     — без прогона тестов (не рекомендуется)
#
# Скрипт ничего не меняет в системе: всё живёт в папке .venv внутри проекта.

set -euo pipefail

WITH_ENGINES=0
RUN_VERIFY=1
for arg in "$@"; do
  case "$arg" in
    --with-engines) WITH_ENGINES=1 ;;
    --no-verify)    RUN_VERIFY=0 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "Неизвестный параметр: $arg (см. --help)" >&2; exit 2 ;;
  esac
done

say()  { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()  { printf '  \033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

say "1/5 Проверяю окружение"

PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python
command -v "$PY" >/dev/null 2>&1 || die "Python не найден. Установите Python 3.9+ и повторите."

PYVER=$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
PYMAJ=$("$PY" -c 'import sys; print(sys.version_info[0])')
PYMIN=$("$PY" -c 'import sys; print(sys.version_info[1])')
if [ "$PYMAJ" -lt 3 ] || { [ "$PYMAJ" -eq 3 ] && [ "$PYMIN" -lt 9 ]; }; then
  die "Нужен Python 3.9 или новее, найден $PYVER."
fi
ok "Python $PYVER ($(command -v "$PY"))"

FREE_MB=$(df -Pm . | awk 'NR==2 {print $4}')
if [ "${FREE_MB:-0}" -lt 400 ]; then
  die "Свободного места ${FREE_MB} МБ — нужно минимум 400 МБ. Освободите диск и повторите."
fi
ok "свободно ${FREE_MB} МБ"

say "2/5 Создаю локальное окружение .venv"
if [ -d .venv ]; then
  warn ".venv уже существует — использую его (удалите папку, если нужна чистая установка)"
else
  if "$PY" -m venv .venv >/tmp/venv_err.$$ 2>&1; then
    ok "создано"
  elif command -v virtualenv >/dev/null 2>&1 && virtualenv -p "$PY" .venv >/dev/null 2>&1; then
    ok "создано через virtualenv"
  else
    SHORT=$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
    echo
    echo "     Причина:"; sed 's/^/       /' /tmp/venv_err.$$ | head -4
    echo
    if grep -qi "ensurepip" /tmp/venv_err.$$ 2>/dev/null; then
      echo "     На Debian/Ubuntu не хватает пакета venv. Варианты:"
      echo "       1) sudo apt install python${SHORT}-venv && ./install.sh"
      echo "       2) pip3 install --user virtualenv && ./install.sh   (если pip не заблокирован PEP 668)"
      echo "       3) без установки вообще: docker build -t geotech-surok . && docker run --rm geotech-surok"
    else
      echo "     Установите пакет venv для Python ${SHORT} и повторите."
    fi
    rm -f /tmp/venv_err.$$
    exit 1
  fi
  rm -f /tmp/venv_err.$$
fi
# shellcheck disable=SC1091
. .venv/bin/activate
ok "активировано: $(command -v python)"

say "3/5 Ставлю зависимости (версии зафиксированы в requirements.lock)"
python -m pip install --upgrade pip -q
python -m pip install -q -r requirements.lock || die "Не удалось поставить зависимости ядра."
ok "ядро установлено"

if [ "$WITH_ENGINES" -eq 1 ]; then
  echo "     ставлю движки (xslope, geoeq)…"
  python -m pip install -q -r requirements-optional.txt || die "Не удалось поставить движки."
  ok "движки установлены (7 методов LEM, давление грунта, подпорные стены)"
else
  warn "движки не ставились (--with-engines добавит 7 методов устойчивости и подпорные стены)"
fi

if [ "$RUN_VERIFY" -eq 1 ]; then
  say "4/5 Проверяю, что всё работает"
  python tools/validate_traceability.py || die "Валидатор трассируемости не прошёл."
  PATTERN=""
  [ "$WITH_ENGINES" -eq 1 ] && PATTERN="-rs"
  python -m pytest -q $PATTERN | tail -3
  ok "проверки пройдены"
else
  say "4/5 Проверки пропущены (--no-verify)"
fi

say "5/5 Готово"
cat <<'TXT'

  Первый расчёт:

      source .venv/bin/activate
      python tools/run_scenario.py scenarios/d1-foundation.yaml

  Ожидаемый результат:
      R = 215.62 кПа,  p = 286.00 кПа,  s = 4.23 см
      проверка p ≤ R — НЕ ВЫПОЛНЯЕТСЯ (+32.6 %)

  Как это выглядит в диалоге с агентом и чем подкреплено — DEMO.md
  Как проверять воспроизводимость шаг за шагом — docs/verify-step-by-step.md

TXT
