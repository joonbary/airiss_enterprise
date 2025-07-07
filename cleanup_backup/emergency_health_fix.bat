@echo off
chcp 65001 >nul
echo AWS EB Health Red 긴급 해결 스크립트
echo ==========================================

echo.
echo 1단계: 현재 상태 확인
eb status

echo.
echo 2단계: 상세 로그 확인
eb logs --all

echo.
echo 3단계: 애플리케이션 재시작
eb restart

echo.
echo 4단계: 헬스 체크
eb health --refresh

echo.
echo 5단계: URL 확인
eb open

echo.
echo 긴급 해결 완료!
pause
