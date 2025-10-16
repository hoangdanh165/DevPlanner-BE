@echo off
REM ---- Run multi-worker ----

REM Worker 1
start "Celery Worker 1" cmd /k celery -A backend worker -l INFO -P solo -n w1@%h

REM Worker 2
start "Celery Worker 2" cmd /k celery -A backend worker -l INFO -P solo -n w2@%h

REM Worker 3
start "Celery Worker 3" cmd /k celery -A backend worker -l INFO -P solo -n w3@%h

REM Worker 4
start "Celery Worker 4" cmd /k celery -A backend worker -l INFO -P solo -n w4@%h

@REM REM Celery Beat (in-memory scheduler)
@REM start "Celery Beat" cmd /k celery -A backend beat -l DEBUG

echo All Celery workers started.
pause