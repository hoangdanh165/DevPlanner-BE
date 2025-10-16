@echo off
REM ---- Stop all Celery workers ----

echo Stopping all Celery workers...

REM Kill theo tên process "celery"
taskkill /F /IM celery.exe >nul 2>&1

REM Kill luôn cửa sổ cmd có title "Celery Worker ..."
taskkill /F /FI "WINDOWTITLE eq Celery Worker*" >nul 2>&1

REM Kill Celery Beat window
taskkill /F /FI "WINDOWTITLE eq Celery Beat" >nul 2>&1

echo All Celery workers stopped.
pause