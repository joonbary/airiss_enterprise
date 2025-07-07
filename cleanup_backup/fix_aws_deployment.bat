@echo off
echo 🚀 AIRISS AWS 배포 문제 해결 스크립트
echo ===============================================

echo.
echo 1️⃣ 현재 상태 확인 중...
python aws_deployment_troubleshoot.py

echo.
echo 2️⃣ EB 상태 확인...
eb status

echo.
echo 3️⃣ EB 헬스 확인...
eb health

echo.
echo 4️⃣ 가능한 해결책:
echo.
echo A. 재배포: eb deploy
echo B. 새 환경: eb create production-v2  
echo C. 로그 확인: eb logs --all
echo D. 환경 종료 후 재생성: eb terminate 후 eb create production
echo.

echo 🎯 권장 해결 순서:
echo 1. eb deploy (재배포)
echo 2. 안 되면 eb logs --all (로그 확인)
echo 3. 그래도 안 되면 eb create production-v2 (새 환경)
echo.

echo 어떤 옵션을 선택하시겠습니까?
echo A) 재배포 (eb deploy)
echo B) 로그 확인 (eb logs)
echo C) 새 환경 생성
echo D) 수동으로 처리
echo.

set /p choice="선택 (A/B/C/D): "

if /i "%choice%"=="A" (
    echo 🔄 재배포 시작...
    eb deploy
    echo ✅ 재배포 완료! 잠시 후 다시 확인하세요.
) else if /i "%choice%"=="B" (
    echo 📋 로그 확인 중...
    eb logs --all
) else if /i "%choice%"=="C" (
    echo 🆕 새 환경 생성 중...
    eb create production-v2
) else (
    echo ℹ️ 수동 처리를 선택했습니다.
    echo AWS Console에서 직접 확인하세요.
)

echo.
echo 🌐 배포 확인 URL: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com
echo 완료 후 위 URL에서 확인하세요!

pause
