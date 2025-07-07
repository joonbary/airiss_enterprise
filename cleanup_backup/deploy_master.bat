@echo off
echo ============================================
echo 🚀 AIRISS v4 AWS 배포 마스터 스크립트
echo ============================================

echo.
echo 사용 가능한 배포 옵션:
echo [1] AWS Amplify (권장 - 가장 간단)
echo [2] AWS Elastic Beanstalk (FastAPI 최적화)
echo [3] AWS EC2 + Docker (고급 사용자)
echo [4] GitHub만 업로드 (배포는 나중에)
echo.

set /p choice="배포 방법을 선택하세요 (1-4): "

if "%choice%"=="1" goto amplify
if "%choice%"=="2" goto beanstalk
if "%choice%"=="3" goto ec2
if "%choice%"=="4" goto github_only
goto invalid

:amplify
echo.
echo 🌟 AWS Amplify 배포 선택됨
echo ============================================
echo 1. GitHub에 코드 업로드
call github_setup_commands.bat
echo.
echo 2. AWS Console 설정 가이드 열기
start aws_amplify_guide.md
echo.
echo ✅ 다음 단계:
echo   1. github_setup_commands.bat 실행 완료 후
echo   2. AWS Console에서 Amplify 설정
echo   3. 배포 URL 확인: https://YOUR-APP-ID.amplifyapp.com
goto end

:beanstalk
echo.
echo 🚀 AWS Elastic Beanstalk 배포 선택됨
echo ============================================
echo 1. GitHub에 코드 업로드
call github_setup_commands.bat
echo.
echo 2. EB CLI 설치 및 설정
echo pip install awsebcli
echo eb init
echo eb create production
echo eb deploy
echo.
echo 3. 설정 가이드 열기
start aws_elasticbeanstalk_guide.md
echo.
echo ✅ Elastic Beanstalk 설정 파일 생성됨:
echo   - application.py
echo   - .ebextensions/ 폴더
goto end

:ec2
echo.
echo 🐳 AWS EC2 + Docker 배포 선택됨
echo ============================================
echo 1. GitHub에 코드 업로드
call github_setup_commands.bat
echo.
echo 2. EC2 설정 가이드 열기
start aws_ec2_docker_guide.md
echo.
echo ✅ Docker 설정 파일 준비됨:
echo   - Dockerfile
echo   - docker-compose.prod.yml
goto end

:github_only
echo.
echo 📚 GitHub 업로드만 진행
echo ============================================
call github_setup_commands.bat
echo.
echo ✅ GitHub 업로드 완료!
echo 나중에 AWS 배포를 원하시면 이 스크립트를 다시 실행하세요.
goto end

:invalid
echo.
echo ❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.
pause
goto start

:end
echo.
echo ============================================
echo 🎉 AIRISS v4 배포 준비 완료!
echo ============================================
echo.
echo 📊 프로젝트 현황:
echo ✅ 8차원 AI 인재 분석 시스템
echo ✅ 실시간 편향 탐지
echo ✅ 하이브리드 AI 모델
echo ✅ 프로덕션 준비 완료
echo.
echo 💡 추가 도움이 필요하시면:
echo   - README.md 참조
echo   - GitHub Issues 활용
echo   - AWS 공식 문서 확인
echo.
echo 🚀 성공적인 배포를 위해 화이팅!
echo ============================================
pause
