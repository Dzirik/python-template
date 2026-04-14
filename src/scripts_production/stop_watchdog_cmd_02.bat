@echo off
setlocal

REM ==========================================
REM CONFIGURATION (EDIT THIS)
REM ==========================================
set TASK_NAME=watchdog_cmd_02
REM ==========================================

echo.
echo ==========================================
echo   Watchdog Restart Tool (%TASK_NAME%)
echo ==========================================
echo.

set /p PID=Enter watchdog PID:

if "%PID%"=="" (
    echo No PID entered. Exiting.
    goto :eof
)

echo.
echo Killing PID %PID% and all child processes...
taskkill /PID %PID% /T /F >nul 2>&1

echo.
choice /C YN /M "Restart %TASK_NAME% now?"
if errorlevel 2 goto :end
if errorlevel 1 goto :restart

:restart
echo.
echo Starting scheduled task "%TASK_NAME%"...
schtasks /run /tn "%TASK_NAME%"

:end
echo.
echo Done.
pause
endlocal
