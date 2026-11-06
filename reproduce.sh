#!/bin/sh
# Reproduce one full public evaluation; never overwrite saved evidence runs.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BENCH_ROOT=${BENCH_ROOT:-"$HERE/../COMP3014J Assignment/student/handover-bench"}
PYTHON=${PYTHON:-"$HERE/.venv/bin/python"}
OUTPUT=${1:-"$HERE/reproduced-$(date +%Y%m%d-%H%M%S)"}
[ -f "$BENCH_ROOT/src/handover_bench/cli.py" ] || { echo 'Set BENCH_ROOT to the supplied handover-bench directory.' >&2; exit 2; }
[ ! -e "$OUTPUT" ] || { echo "Refusing to overwrite existing output: $OUTPUT" >&2; exit 3; }
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export PYTHONPATH="$BENCH_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" -m handover_bench.cli evaluate --algorithm "$HERE/submission/algorithm.py" --suite "$BENCH_ROOT/data/practice" --output "$OUTPUT"
