@echo off
echo ============================================
echo  Speech2Txt Installer
echo ============================================
echo.

:: Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.13 or 3.14.
    pause
    exit /b 1
)

:: Show Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Found %PYVER%

:: Install uv if not available
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv...
    pip install uv
)

:: Create venv if it doesn't exist
if not exist "venv\Scripts\python.exe" (
    echo.
    echo Creating virtual environment...
    uv venv venv --python 3.14
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Install dependencies
echo.
echo Installing dependencies...
uv pip install -r requirements.txt --python venv\Scripts\python.exe
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Installation complete!
echo ============================================
echo.

:: Ask about desktop shortcut
set /p SHORTCUT="Create a desktop shortcut? (Y/N): "
if /i "%SHORTCUT%"=="Y" (
    echo Creating desktop shortcut...
    venv\Scripts\pythonw.exe -c "import os; desktop=os.path.join(os.environ['USERPROFILE'],'Desktop'); venv=os.path.abspath('venv/Scripts/pythonw.exe'); main=os.path.abspath('src/main.py'); wd=os.path.abspath('.'); import subprocess; subprocess.run(['powershell','-Command',f\"$ws=New-Object -ComObject WScript.Shell;$sc=$ws.CreateShortcut('{desktop}\\Speech2Txt.lnk');$sc.TargetPath='{venv}';$sc.Arguments='\\\"{main}\\\"';$sc.WorkingDirectory='{wd}';$sc.Description='Speech2Txt - System-wide dictation';$sc.Save()\"])"
    echo Desktop shortcut created!
)

echo.
echo To run Speech2Txt:
echo   venv\Scripts\pythonw.exe src\main.py
echo.
echo Or use the desktop shortcut if you created one.
echo.
pause
