#!/bin/sh
# Запуск эмулятора с параметром --script-path: выполняется успешный
# стартовый скрипт до команды exit.
set -e
cd "$(dirname "$0")/.."
sh run.sh --script-path examples/start_ok.txt
