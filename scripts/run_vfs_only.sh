#!/bin/sh
# Запуск эмулятора с параметром --vfs-path.
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs-path examples/vfs-stub.csv
