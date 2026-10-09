#!/bin/sh
# Этап 3: ошибки в стартовых скриптах, каждый останавливается на первой ошибке.
# Окна открываются по очереди: закройте окно, чтобы открылось следующее.
set -e
cd "$(dirname "$0")/.."
sh run.sh --vfs-path examples/vfs/files.csv --script-path examples/start_error.txt
sh run.sh --vfs-path examples/vfs/files.csv --script-path examples/start_quote_error.txt
sh run.sh --vfs-path examples/vfs/files.csv --script-path examples/start_exit_error.txt
sh run.sh --vfs-path examples/vfs/files.csv --script-path examples/start_conf_error.txt
