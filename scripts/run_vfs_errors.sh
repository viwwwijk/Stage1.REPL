#!/bin/sh
# Этап 3: ошибки загрузки VFS (нет файла, неверный заголовок, неверный base64).
# Окна открываются по очереди: закройте окно, чтобы открылось следующее.
set -e
cd "$(dirname "$0")/.."
sh run.sh --vfs-path examples/vfs/missing.csv --script-path examples/vfs_show.txt
sh run.sh --vfs-path examples/vfs/broken_header.csv --script-path examples/vfs_show.txt
sh run.sh --vfs-path examples/vfs/broken_base64.csv --script-path examples/vfs_show.txt
