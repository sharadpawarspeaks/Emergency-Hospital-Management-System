@echo off
title Hospital Emergency Management System
echo Launching Hospital Emergency Management System...
py main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying direct python path...
    "C:\Users\pawar\AppData\Local\Python\bin\python.exe" main.py
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)
