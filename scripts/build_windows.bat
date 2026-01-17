@echo off
REM Windows build script for VideoDub

echo === Building VideoDub for Windows ===

REM Check if we're on Windows
ver | findstr /i "Microsoft Windows" >nul
if %errorlevel% neq 0 (
    echo Error: This script must be run on Windows
    exit /b 1
)

REM Install Nuitka if not present
python -m nuitka --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Nuitka...
    pip install nuitka ordered-set zstandard
)

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build executable
echo Building VideoDub executable...
python build.py

REM Check if build succeeded
if exist "dist\videodub.exe" (
    echo Build successful!
    dir dist\
) else (
    echo Build failed!
    exit /b 1
)

pause