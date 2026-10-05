@echo off
rem Этап 3: VFS из нескольких файлов, включая двоичный (base64).
cd /d "%~dp0.."
call run.bat --vfs-path examples\vfs\files.csv --script-path examples\vfs_show.txt
