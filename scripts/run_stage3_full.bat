@echo off
rem Этап 3: стартовый скрипт со всеми командами этапов 1-3 на глубокой VFS.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\deep.csv --script-path examples\start_stage3.txt
