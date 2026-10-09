#!/bin/sh
# Этап 3: VFS с вложенностью не менее 3 уровней файлов и папок.
set -e
cd "$(dirname "$0")/.."
sh run.sh --vfs-path examples/vfs/deep.csv --script-path examples/vfs_show.txt
