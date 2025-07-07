@echo off
echo ==========================================
echo AIRISS 완전 배포 시작
echo ==========================================

echo 현재 디렉토리 확인...
cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo 배포 시작...
eb deploy

echo 배포 상태 확인...
eb status

echo 애플리케이션 열기...
eb open

echo ==========================================
echo 배포 완료! 브라우저에서 확인하세요.
echo ==========================================
pause
