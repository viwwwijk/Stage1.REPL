#!/bin/sh
# Этап 5: все режимы rmdir, изменения VFS только в памяти.
set -e
cd "$(dirname "$0")/.."
sh run.sh --vfs-path examples/vfs/rmdir.csv --script-path examples/start_stage5.txt
