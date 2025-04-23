@echo off
echo Starting Screen Icon Detector - Configuration Editor
echo ==================================================
echo.

:: Launch the editor using the run_editor.py script
python src\run_editor.py

:: Check for errors
if %errorlevel% neq 0 (
    echo.
    echo Error: The editor could not be started.
    echo Please run setup.bat first to ensure all dependencies are installed.
    pause
    exit /b 1
)

exit /b 0
