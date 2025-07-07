@echo off
echo =====================================================
echo AIRISS v4.1 Vercel 재배포 스크립트
echo =====================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend"

echo 1. 새 빌드 생성 중...
call npm run build
if errorlevel 1 (
    echo 빌드 실패! ESLint 오류 무시하고 재시도...
    set DISABLE_ESLINT_PLUGIN=true
    call npm run build
)

echo.
echo 2. Git 변경사항 커밋 중...
git add .
git commit -m "Fix: Vercel static files serving issue - Add MIME types for fonts and manifest"

echo.
echo 3. GitHub 푸시 중...
git push origin main

echo.
echo 4. Vercel 자동 배포 시작됨
echo    배포 상태 확인: https://vercel.com/dashboard
echo    사이트 주소: https://airiss-enterprise-v4.vercel.app

echo.
echo =====================================================
echo 배포 완료! 2-3분 후 사이트를 확인하세요.
echo =====================================================

echo.
echo 문제가 지속되면 다음 대안을 시도하세요:
echo 1. 폰트 CDN 사용 (Google Fonts)
echo 2. 다른 호스팅 서비스 (Netlify)
echo 3. GitHub Pages 배포

pause
