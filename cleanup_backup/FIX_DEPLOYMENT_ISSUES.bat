@echo off
echo ==========================================
echo AIRISS 배포 오류 진단 및 수정
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo 1. 현재 배포 상태 확인...
eb status

echo 2. 배포 로그 확인...
eb logs --all

echo 3. 헬스 체크 상태...
eb health

echo 4. 환경 재시작...
eb restart

echo 5. 재배포 시도...
eb deploy

echo ==========================================
echo 문제 해결 완료 시도
echo ==========================================
pause
