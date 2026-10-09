#!/bin/sh
# Этап 3: минимальная VFS (один файл в корне).
set -e
cd "$(dirname "$0")/.."
sh run.sh --vfs-path examples/vfs/minimal.csv --script-path examples/vfs_show.txt
