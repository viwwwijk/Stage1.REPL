#!/bin/sh
# Запуск эмулятора с параметром --vfs-path.
set -e
cd "$(dirname "$0")/.."
sh run.sh --vfs-path examples/vfs/minimal.csv
