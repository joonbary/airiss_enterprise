@echo off
chcp 65001 >nul
echo 🚨 AIRISS Health Red 즉시 해결 스크립트
echo ================================================

echo.
echo ⏰ %date% %time%
echo 📍 현재 위치: %cd%

echo.
echo 1️⃣ 현재 EB 상태 확인
eb status

echo.
echo 2️⃣ 상세 헬스 정보 조회
eb health --refresh

echo.
echo 3️⃣ 최근 로그 확인 (마지막 100줄)
eb logs --all | tail -100

echo.
echo 4️⃣ 애플리케이션 재시작 시도
eb restart

echo.
echo ⏳ 30초 대기 (재시작 완료 대기)
timeout /t 30 /nobreak

echo.
echo 5️⃣ 재시작 후 상태 확인
eb health --refresh

echo.
echo 6️⃣ URL 테스트
eb open

echo.
echo ✅ 즉시 해결 시도 완료!
echo 📋 Health가 여전히 Red면 로그를 확인하여 근본 원인 파악 필요
pause
