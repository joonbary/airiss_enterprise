@echo off
chcp 65001 >nul
echo 🚨 AIRISS Health Red 완전 해결 스크립트
echo =============================================
echo 강화된 헬스체크로 Health Red 근본 해결
echo.

echo ⏰ 시작 시간: %date% %time%
echo 📍 현재 위치: %cd%
echo.

echo 📋 Step 1: 현재 상태 진단
echo ---------------------------
eb status
eb health --refresh

echo.
echo 📋 Step 2: 강화된 application.py 적용
echo ------------------------------------
echo 기존 application.py 백업 중...
copy application.py application_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.py

echo 강화된 버전으로 교체...
copy application_health_enhanced.py application.py

echo 강화된 requirements.txt 적용...
copy requirements_health_enhanced.txt requirements.txt

echo.
echo 📋 Step 3: 새 버전 배포
echo ----------------------
eb deploy --timeout=10

echo.
echo ⏳ 배포 완료 대기 (60초)...
timeout /t 60 /nobreak

echo.
echo 📋 Step 4: 배포 후 상태 확인
echo --------------------------
eb status
eb health --refresh

echo.
echo 📋 Step 5: 엔드포인트 테스트
echo -------------------------
echo 1. Root endpoint test:
curl -s "http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com/" | head -5

echo.
echo 2. Health endpoint test:
curl -s "http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com/health"

echo.
echo 3. Status endpoint test:
curl -s "http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com/status"

echo.
echo 📋 Step 6: 최종 결과
echo ------------------
eb health --refresh

echo.
if "%ERRORLEVEL%"=="0" (
    echo ✅ Health Red 해결 완료!
    echo 🎯 모든 엔드포인트가 정상 작동 중입니다.
) else (
    echo ❌ 여전히 문제가 있습니다.
    echo 📊 로그를 확인해주세요: eb logs --all
)

echo.
echo 📞 추가 지원이 필요하면 상세 로그를 확인하세요.
echo 💡 eb logs --all ^| findstr ERROR
echo.

pause
