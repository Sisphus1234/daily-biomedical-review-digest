@echo off
chcp 65001 >nul
cd /d E:\test
python -m src.main --commit >> run_log.txt 2>&1