#!/bin/sh
# Group 25: evaluate the canonical submission/algorithm.py, not historical V10.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BENCH_ROOT=$(CDPATH= cd -- "${BENCH_ROOT:-$HERE/course/benchmark}" && pwd)
PYTHON=${PYTHON:-python3}
OUTPUT=${1:-"$HERE/reproduced-public"}
[ ! -e "$OUTPUT" ] || { echo "Choose a new output directory: $OUTPUT" >&2; exit 3; }
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export PYTHONPATH="$BENCH_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON" -m handover_bench.cli evaluate --algorithm "$HERE/submission/algorithm.py" --suite "$BENCH_ROOT/data/practice" --output "$OUTPUT/queue"
"$PYTHON" -m handover_bench.cli evaluate --algorithm "$BENCH_ROOT/examples/algorithm.py" --suite "$BENCH_ROOT/data/practice" --output "$OUTPUT/starter"
"$PYTHON" "$HERE/tools/table2.py" "$OUTPUT" "$HERE/submission/algorithm.py"
