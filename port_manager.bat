@echo off
echo ================================================================================
echo  AIRISS v4.1 포트 관리 도구
echo ================================================================================
echo.

:menu
echo 1. 포트 8002 사용 중인 프로세스 확인
echo 2. 포트 8002 강제 종료
echo 3. 다른 포트로 AIRISS 실행
echo 4. 종료
echo.
set /p choice="선택하세요 (1-4): "

if "%choice%"=="1" goto check_port
if "%choice%"=="2" goto kill_port
if "%choice%"=="3" goto run_auto
if "%choice%"=="4" goto end

:check_port
echo.
echo 🔍 포트 8002 확인 중...
echo ----------------------------------------
netstat -ano | findstr :8002
echo ----------------------------------------
echo.
echo 💡 맨 오른쪽 숫자가 PID(프로세스 ID)입니다.
echo.
pause
goto menu

:kill_port
echo.
set /p pid="종료할 프로세스 PID를 입력하세요: "
echo.
echo ⚠️ PID %pid% 프로세스를 종료합니다...
taskkill /PID %pid% /F
echo.
if errorlevel 1 (
    echo ❌ 프로세스 종료 실패. 관리자 권한으로 실행하세요.
) else (
    echo ✅ 프로세스가 종료되었습니다.
)
echo.
pause
goto menu

:run_auto
echo.
echo 🚀 사용 가능한 포트를 자동으로 찾아 AIRISS를 실행합니다...
echo.
python run_auto_port.py
pause
goto menu

:end
echo.
echo 👋 프로그램을 종료합니다.
pause
