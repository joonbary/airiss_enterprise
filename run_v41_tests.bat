@echo off
echo ========================================
echo AIRISS v4.1 Enhanced Test Suite
echo Deep Learning Edition
echo ========================================
echo.

REM Python 가상환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
    echo [OK] 가상환경 활성화됨
) else (
    echo [WARNING] 가상환경이 없습니다
)

echo.
echo [1/3] 테스트 데이터 생성 중...
python generate_bulk_test.py

echo.
echo [2/3] 필요 패키지 확인...
pip install aiohttp pandas openpyxl --quiet

echo.
echo [3/3] 통합 테스트 실행...
python test_v41_integration.py

echo.
echo ========================================
echo 테스트 완료! 
echo test_report_*.json 파일을 확인하세요.
echo ========================================
pause