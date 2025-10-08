@echo off
echo Installing Selenium and WebDriver Manager...
echo.

REM Find Python in venv
set PYTHON_PATH=venv\Scripts\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Error: Python not found in venv\Scripts\
    echo Please create a new virtual environment
    pause
    exit /b 1
)

REM Install packages
echo Installing selenium...
"%PYTHON_PATH%" -m pip install --upgrade pip
"%PYTHON_PATH%" -m pip install selenium==4.15.2
"%PYTHON_PATH%" -m pip install webdriver-manager==4.0.1

echo.
echo Installation complete!
echo You can now use the scraping feature in the admin panel.
echo.
pause

