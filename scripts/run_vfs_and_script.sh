#!/bin/sh
# Запуск эмулятора с обоими параметрами одновременно: стартовый
# скрипт останавливается на первой ошибке (команда mkdir).
set -e
cd "$(dirname "$0")/.."
sh run.sh --vfs-path examples/vfs/minimal.csv --script-path examples/start_error.txt
