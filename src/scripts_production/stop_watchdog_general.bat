@echo off
setlocal

REM ==========================================
REM USAGE: stop_watchdog_general.bat <task_name>
REM <task_name> is both the watchdog config name (heartbeats_<task_name>\watchdog.pid) and the
REM Task Scheduler task name used for the optional restart. If omitted, you will be prompted.
REM ==========================================

set TASK_NAME=%~1
if "%TASK_NAME%"=="" set /p TASK_NAME=Enter watchdog config / task name (e.g. watchdog_cmd_01):

if "%TASK_NAME%"=="" (
    echo No config/task name entered. Exiting.
    goto :eof
)

set SCRIPT_DIR=%~dp0
set PID_FILE=%SCRIPT_DIR%heartbeats_%TASK_NAME%\watchdog.pid

echo.
echo ==========================================
echo   Watchdog kill / optional restart tool (%TASK_NAME%)
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
taskkill /PID %PID% /T /F

echo.
choice /C YN /M "Do you want to start the watchdog again via Task Scheduler"
if errorlevel 2 goto :end
if errorlevel 1 goto :start_task

:start_task
echo.
echo Starting scheduled task "%TASK_NAME%"...
schtasks /run /tn "%TASK_NAME%"

goto :end

:end
echo.
echo Done.
pause
endlocal
