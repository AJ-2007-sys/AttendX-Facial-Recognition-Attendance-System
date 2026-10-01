@echo off
setlocal
title AttendX - Face Recognition Attendance System
chcp 65001 >nul 2>&1
cls

:: Generate the Escape character to make ANSI colors work in CMD
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

echo.
echo  %ESC%[38;5;208m* * *%ESC%[0m  AttendX v1.0
echo   %ESC%[38;5;214m* * *%ESC%[0m Face Recognition Attendance System
echo    %ESC%[38;5;220m* * *%ESC%[0m
echo.
echo  %ESC%[90mServer   %ESC%[37mhttp://localhost:8000%ESC%[0m
echo  %ESC%[90mMode     %ESC%[37mDevelopment%ESC%[0m
echo  %ESC%[90mBackend  %ESC%[37mFastAPI + Uvicorn%ESC%[0m
echo.
echo  %ESC%[90m-----------------------------------------%ESC%[0m
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python app.py
pause
