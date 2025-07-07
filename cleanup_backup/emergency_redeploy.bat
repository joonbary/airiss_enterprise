@echo off
chcp 65001 >nul
echo AIRISS v4 긴급 복구 및 재배포
echo =================================

echo.
echo 1단계: 현재 상태 백업
copy Procfile Procfile_before_emergency_fix

echo.
echo 2단계: 더 안전한 Procfile 적용
copy Procfile_emergency_simple Procfile

echo.
echo 3단계: 긴급 재배포
eb deploy --timeout 15

echo.
echo 4단계: 상태 확인
eb status
eb health --refresh

echo.
echo 5단계: 로그 확인
eb logs --all

echo.
echo 긴급 복구 완료!
echo URL 확인:
eb open

pause
