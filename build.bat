@echo off
echo Building Speech2Txt...
call venv\Scripts\activate
pip install pyinstaller
pyinstaller --onefile --noconsole --name Speech2Txt src\main.py
echo.
echo Build complete! Executable is at dist\Speech2Txt.exe
pause
