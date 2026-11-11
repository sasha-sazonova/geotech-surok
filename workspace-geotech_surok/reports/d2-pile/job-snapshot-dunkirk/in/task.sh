#!/bin/bash
set -u
OUTD="$(cd ../out && pwd)"
~/geotech-jobs/venvs/piles-py310/bin/python task.py > "$OUTD/d2_dunkirk_stdout.txt" 2> "$OUTD/d2_dunkirk_err.txt"
echo dunk-done
