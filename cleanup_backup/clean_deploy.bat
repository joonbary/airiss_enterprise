@echo off
echo ===================================
echo AIRISS v4.0 클린 배포 시작
echo ===================================

echo 1. 기존 배포 파일 정리...
if exist .elasticbeanstalk\app_versions rmdir /s /q .elasticbeanstalk\app_versions
if exist .elasticbeanstalk\logs rmdir /s /q .elasticbeanstalk\logs

echo 2. 강제 배포 시작...
eb deploy --label "airiss-simple-%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%" --timeout 10

echo 3. 배포 상태 확인...
eb status

echo 4. Health check...
eb health

echo 5. 최신 로그 확인...
eb logs --all

echo ===================================
echo 배포 완료
echo ===================================
pause