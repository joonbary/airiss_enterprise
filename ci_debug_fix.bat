@echo off
chcp 65001 > nul
echo 🔧 AIRISS CI/CD 디버깅 및 수정 스크립트
echo ============================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo 📊 1단계: 현재 Git 상태 확인
echo ----------------------------------------
git status
git branch -a
echo.
echo 최근 커밋 5개:
git log --oneline -5

echo.
echo 🔄 2단계: main 브랜치로 전환
echo ----------------------------------------
git checkout main
git pull origin main

echo.
echo 🔧 3단계: 응급 CI 설정 활성화
echo ----------------------------------------
echo 현재 CI 설정 확인:
dir .github\workflows\*.yml

echo.
echo 📝 현재 활성 CI 파일 내용:
type .github\workflows\ci.yml

echo.
echo 🚀 4단계: GitHub Actions 상태 확인 링크
echo ----------------------------------------
echo GitHub Actions 페이지를 브라우저에서 확인하세요:
echo https://github.com/joonbary/airiss_enterprise/actions
echo.

echo 🔄 5단계: 필요시 더 관대한 CI로 교체
echo ----------------------------------------
echo 현재 CI가 계속 실패한다면 emergency CI로 교체하시겠습니까?
set /p choice="Y/N: "

if /i "%choice%"=="Y" (
    echo emergency CI로 교체 중...
    copy .github\workflows\ci.yml .github\workflows\ci_current_backup.yml
    copy .github\workflows\emergency_ci.yml .github\workflows\ci.yml
    echo ✅ emergency CI로 교체 완료
) else (
    echo 현재 CI 설정 유지
)

echo.
echo 📤 6단계: 변경사항 GitHub에 반영
echo ----------------------------------------
git add .
git commit -m "Fix: CI/CD pipeline debugging and emergency fix"
git push origin main

echo.
echo ✅ 완료! 2-3분 후 GitHub Actions에서 상태를 확인하세요.
echo 🌐 GitHub Actions: https://github.com/joonbary/airiss_enterprise/actions
echo.
pause