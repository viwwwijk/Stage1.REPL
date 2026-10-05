@echo off
rem Этап 3: минимальная VFS (один файл в корне).
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\minimal.csv --script-path examples\vfs_show.txt
