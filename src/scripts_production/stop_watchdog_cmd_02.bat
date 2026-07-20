@echo off
setlocal

REM ==========================================
REM CONFIGURATION (EDIT THIS)
REM ==========================================
set TASK_NAME=watchdog_cmd_02
REM ==========================================

set SCRIPT_DIR=%~dp0
set PID_FILE=%SCRIPT_DIR%heartbeats_%TASK_NAME%\watchdog.pid

echo.
echo ==========================================
echo   Watchdog Restart Tool (%TASK_NAME%)
echo ==========================================
echo.

set PID=
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    echo Found watchdog PID %PID% in "%PID_FILE%".
) else (
    echo PID file not found: "%PID_FILE%"
    set /p PID=Enter watchdog PID:
)

if "%PID%"=="" (
    echo No PID available. Exiting.
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
