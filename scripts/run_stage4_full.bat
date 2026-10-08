@echo off
rem Этап 4: все режимы ls, cd, find и wc на VFS с 4 уровнями вложенности.
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\deep.csv --script-path examples\start_stage4.txt
