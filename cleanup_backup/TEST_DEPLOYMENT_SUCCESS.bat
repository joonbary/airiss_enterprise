@echo off
echo ==========================================
echo AIRISS 배포 성공 테스트
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo 1. 배포 상태 확인...
eb status

echo 2. URL 가져오기...
for /f "tokens=2 delims=: " %%a in ('eb status ^| findstr "CNAME"') do set URL=%%a

echo 3. 헬스 체크 테스트...
curl -s "%URL%/health" || echo "Health check failed"

echo 4. 상태 API 테스트...
curl -s "%URL%/status" || echo "Status API failed"

echo 5. 메인 페이지 테스트...
curl -s -I "%URL%/" || echo "Main page failed"

echo 6. 브라우저에서 열기...
eb open

echo ==========================================
echo 배포 URL: %URL%
echo 모든 테스트 완료!
echo ==========================================
pause
