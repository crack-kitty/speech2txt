@echo off
echo ============================================
echo  Speech2Txt — Full Installer Build
echo ============================================
echo.

:: Step 1: Build the exe with PyInstaller
echo [1/2] Building Speech2Txt.exe with PyInstaller...
call venv\Scripts\activate
uv pip install pyinstaller --python venv\Scripts\python.exe
pyinstaller speech2txt.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)
echo.

:: Step 2: Build the installer with Inno Setup
echo [2/2] Building installer with Inno Setup...
where iscc >nul 2>nul
if errorlevel 1 (
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    ) else (
        echo ERROR: Inno Setup not found!
        echo Install it with: choco install innosetup -y
        echo Or download from: https://jrsoftware.org/isdl.php
        pause
        exit /b 1
    )
) else (
    iscc installer.iss
)
if errorlevel 1 (
    echo ERROR: Inno Setup build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Build complete!
echo  Installer: installer\Speech2Txt-Setup.exe
echo ============================================
pause
