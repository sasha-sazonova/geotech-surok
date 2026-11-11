#!/bin/bash
set -u
OUTD="$(cd ../out && pwd)"
~/geotech-jobs/venvs/piles-py310/bin/python task.py > "$OUTD/d2_stdout.txt" 2> "$OUTD/d2_err.txt"
echo d2-final-done
