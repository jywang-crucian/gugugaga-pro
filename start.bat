@echo off
setlocal

cd /d "%~dp0"

echo Starting AI Talk Desktop...

if exist ".venv\Scripts\python.exe" (
  set "PY_EXE=.venv\Scripts\python.exe"
) else (
  set "PY_EXE=python"
)

if "%DEEPSEEK_API_KEY%"=="" (
  echo.
  echo [WARN] DEEPSEEK_API_KEY is not set.
  echo Please set it in PowerShell first:
  echo   setx DEEPSEEK_API_KEY "your_api_key"
  echo Then reopen terminal and run again.
  echo.
)

"%PY_EXE%" -m pip show openai >nul 2>nul
if errorlevel 1 (
  echo [INFO] Installing dependencies...
  "%PY_EXE%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
  )
)

"%PY_EXE%" app_desktop.py
if errorlevel 1 (
  echo.
  echo Application exited with an error.
  pause
)

endlocal
