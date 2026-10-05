#!/bin/sh
# Этап 3: VFS из нескольких файлов, включая двоичный (base64).
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs-path examples/vfs/files.csv --script-path examples/vfs_show.txt
