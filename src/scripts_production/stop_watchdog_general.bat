@echo off
setlocal

echo.
echo ==========================================
echo   Watchdog kill / optional restart tool
echo ==========================================
echo.

set /p PID=Enter watchdog PID:

if "%PID%"=="" (
    echo No PID entered. Exiting.
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
set /p TASKNAME=Enter Task Scheduler task name:

if "%TASKNAME%"=="" (
    echo No task name entered. Exiting without restart.
    goto :eof
)

echo.
echo Starting scheduled task "%TASKNAME%"...
schtasks /run /tn "%TASKNAME%"

goto :end

:end
echo.
echo Done.
pause
endlocal
