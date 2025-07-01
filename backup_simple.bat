@echo off
REM AIRISS 간단 백업 스크립트 (Windows)

echo 🔄 AIRISS 백업 시작...

REM 날짜 설정
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set mydate=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a-%%b
set timestamp=%mydate%_%mytime%

REM 백업 디렉토리 생성
if not exist "backups" mkdir backups
if not exist "backups\%mydate%" mkdir "backups\%mydate%"

echo 📦 프로젝트 압축 중...

REM 7-Zip이 있으면 사용 (없으면 PowerShell 사용)
where 7z >nul 2>nul
if %errorlevel%==0 (
    7z a "backups\%mydate%\airiss_backup_%timestamp%.7z" ^
       -xr!.git ^
       -xr!__pycache__ ^
       -xr!venv ^
       -xr!node_modules ^
       -xr!logs ^
       -xr!temp_data ^
       -xr!uploads ^
       -xr!*.pyc ^
       -xr!*.log ^
       *
) else (
    REM PowerShell로 압축
    powershell -Command "Compress-Archive -Path . -DestinationPath 'backups\%mydate%\airiss_backup_%timestamp%.zip' -Force"
)

REM 데이터베이스 별도 복사
if exist "airiss.db" (
    copy "airiss.db" "backups\%mydate%\airiss_db_%timestamp%.db"
    echo 💾 데이터베이스 백업 완료
)

echo ✅ 백업 완료: backups\%mydate%\airiss_backup_%timestamp%
echo 📁 백업 위치: %cd%\backups\%mydate%

REM 30일 이상 된 백업 폴더 정리 (선택사항)
forfiles /p backups /d -30 /c "cmd /c if @isdir==TRUE rmdir /s /q @path" 2>nul

pause
