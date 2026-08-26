@echo off
chcp 65001 >nul
cd /d E:\test
python -m src.vocab_main --commit >> run_vocab_log.txt 2>&1
