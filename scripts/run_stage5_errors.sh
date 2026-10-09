#!/bin/sh
# Этап 5: ошибки rmdir, по одному стартовому скрипту на случай.
# Окна открываются по очереди: закройте окно, чтобы открылось следующее.
set -e
cd "$(dirname "$0")/.."
for script in examples/stage5_errors/*.txt; do
    sh run.sh --vfs-path examples/vfs/rmdir.csv --script-path "$script"
done
