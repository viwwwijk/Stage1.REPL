@echo off
rem Этап 5: все режимы rmdir, изменения VFS только в памяти.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\rmdir.csv --script-path examples\start_stage5.txt
