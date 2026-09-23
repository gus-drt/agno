@echo off
echo ==============================================
echo Iniciando o Agno (Telegram Bridge)...
echo Pressione Ctrl+C para encerrar.
echo ==============================================
pushd "%~dp0"
call venv\Scripts\python.exe main.py
popd
