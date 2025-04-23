@echo off
echo Starting Screen Icon Detector - Automation
echo ========================================
echo.

:: Launch the automation using launch.py
python src\launch.py --automation-only

:: Check for errors
if %errorlevel% neq 0 (
    echo.
    echo Error: The automation could not be started.
    echo Please run setup.bat first and ensure your configuration is set up correctly.
    echo You can set up your configuration by running editor.bat
    pause
    exit /b 1
)

exit /b 0
