#!/bin/sh
# Этап 4: все режимы ls, cd, find и wc на VFS с 4 уровнями вложенности.
set -e
cd "$(dirname "$0")/.."
./run.sh --vfs-path examples/vfs/deep.csv --script-path examples/start_stage4.txt
