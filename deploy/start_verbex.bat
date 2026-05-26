@echo off
REM ===================================================================
REM VERBEX MVP (Python) · Arranque del agente normalizador
REM ===================================================================
REM Lanza los 2 procesos del MVP en Python puro (sin n8n):
REM   1. Bot Telegram   (telegram_bot.py)        -> escucha POs
REM   2. Dashboard      (streamlit dashboard)    -> http://localhost:8501
REM
REM Cada uno en su propia ventana cmd.exe para que el operador pueda
REM verlos y cerrarlos individualmente.
REM
REM Uso: doble clic sobre este .bat (o lanzado desde Task Scheduler).
REM Requiere: Python 3.10+ en PATH, dependencias instaladas y .env relleno.
REM Si usas venv, edita la linea SET PY de abajo.
REM ===================================================================

setlocal

REM Raiz del repo = carpeta padre de deploy\
set "REPO_ROOT=%~dp0.."

REM Interprete de Python. Si usas venv, apunta aqui a su python.exe, p.ej.:
REM   set "PY=%REPO_ROOT%\.venv\Scripts\python.exe"
set "PY=python"

echo.
echo ===================================================================
echo   VERBEX MVP (Python) - arranque
echo   Repo: %REPO_ROOT%
echo ===================================================================
echo.

REM --- 1. Bot Telegram -----------------------------------------------
echo [1/2] Lanzando bot de Telegram...
start "VERBEX Bot" cmd /k "cd /d %REPO_ROOT% && %PY% telegram_bot.py"
timeout /t 3 /nobreak > nul

REM --- 2. Dashboard Streamlit ----------------------------------------
echo [2/2] Lanzando dashboard...
start "VERBEX Dashboard" cmd /k "cd /d %REPO_ROOT% && %PY% -m streamlit run dashboard\app.py"
timeout /t 4 /nobreak > nul

echo.
echo ===================================================================
echo   VERBEX MVP arrancado.
echo.
echo   - Bot Telegram: escuchando (ventana "VERBEX Bot")
echo   - Dashboard:    http://localhost:8501
echo ===================================================================
echo.
echo Pulsa una tecla para cerrar esta ventana de log
echo (los 2 procesos siguen corriendo en sus propias ventanas).
pause > nul
endlocal
