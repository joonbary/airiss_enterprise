@echo off
echo ========================================
echo  AIRISS AWS 배포 수정 스크립트
echo ========================================

echo.
echo 1. 현재 Procfile 백업...
copy Procfile Procfile_backup_%date:~0,4%%date:~5,2%%date:~8,2%.txt

echo.
echo 배포 수정 옵션을 선택하세요:
echo 1) 안정화된 Procfile 사용 (권장)
echo 2) 간단한 Uvicorn Procfile 사용  
echo 3) 디버깅 강화 버전 사용
echo 4) 모든 옵션 순차 시도

set /p choice="선택 (1-4): "

if "%choice%"=="1" goto stable
if "%choice%"=="2" goto simple  
if "%choice%"=="3" goto debug
if "%choice%"=="4" goto all
goto end

:stable
echo.
echo [옵션 1] 안정화된 Procfile 적용...
copy Procfile_stable Procfile
echo ✅ 안정화된 Procfile 적용 완료
goto deploy

:simple
echo.
echo [옵션 2] 간단한 Uvicorn Procfile 적용...
copy Procfile_simple Procfile
echo ✅ 간단한 Procfile 적용 완료
goto deploy

:debug
echo.
echo [옵션 3] 디버깅 강화 버전 적용...
copy application_debug.py application.py
copy Procfile_stable Procfile
echo ✅ 디버깅 버전 적용 완료
goto deploy

:all
echo.
echo [옵션 4] 모든 옵션 순차 시도...
echo 첫 번째: 안정화 Procfile 시도
copy Procfile_stable Procfile
goto deploy

:deploy
echo.
echo 2. AWS 배포 시작...
eb deploy

echo.
echo 3. 배포 상태 확인...
eb status

echo.
echo 4. 로그 확인 (문제 발생 시)...
echo eb logs 명령어로 로그를 확인하세요.

echo.
echo ========================================
echo 배포 완료! 
echo 웹사이트 확인: eb open
echo 로그 확인: eb logs  
echo 상태 확인: eb status
echo ========================================

:end
pause
