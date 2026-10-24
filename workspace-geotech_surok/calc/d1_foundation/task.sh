#!/bin/bash
set -u
OUTD="$(cd ../out && pwd)"
export PATH="$HOME/geotech-jobs/venvs/geotech-base/bin:$PATH"
PY="$HOME/geotech-jobs/venvs/geotech-base/bin/python"
"$PY" calc_main.py > "$OUTD/result_main.json" 2> "$OUTD/err_main.txt"
"$PY" calc_check.py > "$OUTD/result_check.json" 2> "$OUTD/err_check.txt"
"$PY" compare.py > "$OUTD/result_compare.json" 2> "$OUTD/err_compare.txt"
echo "d1-v2 done"
