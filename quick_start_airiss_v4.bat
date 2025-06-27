@echo off
echo ============================================================
echo AIRISS v4.0 빠른 실행 스크립트
echo ============================================================
echo.

echo [1/4] scikit-learn 설치 확인...
python -c "import sklearn; print('✅ scikit-learn 설치됨')" 2>nul || (
    echo scikit-learn 설치 중...
    pip install scikit-learn
)

echo.
echo [2/4] 서버 컴포넌트 테스트...
python test_server_components.py

echo.
echo [3/4] 서버 시작 준비 완료!
echo.
echo 서버를 시작하려면 아무 키나 누르세요...
pause >nul

echo.
echo [4/4] AIRISS v4.0 서버 시작...
start cmd /k start_enhanced_v4.bat

echo.
echo 5초 후 브라우저에서 AIRISS v4.0을 열겠습니다...
timeout /t 5 /nobreak >nul

echo.
echo 웹 브라우저 열기...
start http://localhost:8002/

echo.
echo ============================================================
echo AIRISS v4.0이 시작되었습니다!
echo.
echo - 메인 UI: http://localhost:8002/
echo - API 문서: http://localhost:8002/docs
echo - 대시보드: http://localhost:8002/dashboard
echo.
echo 통합 테스트를 실행하려면 새 터미널에서:
echo   python test_airiss_v4_integration.py
echo ============================================================
pause
