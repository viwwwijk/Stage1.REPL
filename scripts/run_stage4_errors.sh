#!/bin/sh
# Этап 4: ошибки ls, cd, find и wc, по одному стартовому скрипту на случай.
# Окна открываются по очереди: закройте окно, чтобы открылось следующее.
set -e
cd "$(dirname "$0")/.."
for script in examples/stage4_errors/*.txt; do
    ./run.sh --vfs-path examples/vfs/deep.csv --script-path "$script"
done
