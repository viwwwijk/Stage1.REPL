#!/bin/sh
# Этап 3: стартовый скрипт со всеми командами этапов 1-3 на глубокой VFS.
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs-path examples/vfs/deep.csv --script-path examples/start_stage3.txt
