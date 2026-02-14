@echo off
echo Building Speech2Txt...
call venv\Scripts\activate
pip install pyinstaller
pyinstaller speech2txt.spec
echo.
echo Build complete! Executable is at dist\Speech2Txt.exe
pause
