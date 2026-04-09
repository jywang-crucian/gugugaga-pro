@echo off
setlocal

cd /d "%~dp0"

echo [1/4] Checking Python...
python --version >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found in PATH.
  pause
  exit /b 1
)

echo [2/4] Installing build dependencies...
python -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip.
  pause
  exit /b 1
)

python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo [ERROR] Failed to install dependencies.
  pause
  exit /b 1
)

echo [3/4] Cleaning old build outputs...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "AI-Talk-Desktop.spec" del /q "AI-Talk-Desktop.spec"

echo [4/4] Building Windows executable...
pyinstaller --noconfirm --onefile --windowed --name "AI-Talk-Desktop" app_desktop.py
if errorlevel 1 (
  echo [ERROR] Build failed.
  pause
  exit /b 1
)

echo.
echo Build success: dist\AI-Talk-Desktop.exe
echo.
pause
endlocal
