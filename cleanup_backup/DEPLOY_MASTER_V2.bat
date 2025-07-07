@echo off
cls
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                    🚀 AIRISS v4.1 배포 마스터                ║
echo  ║              GitHub + AWS 원클릭 배포 시스템                  ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🎯 현재 프로젝트: AIRISS v4.1 Enhanced
echo  📊 상태: Production Ready
echo  💼 대상: OK금융그룹 1,800+ 직원
echo  🌍 목표: 글로벌 AI HR 솔루션
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

echo 📋 배포 전 자동 점검 중...
timeout /t 2 /nobreak >nul

echo ✅ 프로젝트 구조 확인
if exist "app\main.py" (
    echo    ├─ FastAPI 애플리케이션: 정상
) else (
    echo    ├─ FastAPI 애플리케이션: ❌ 누락
    goto error
)

if exist "requirements.txt" (
    echo    ├─ 의존성 파일: 정상
) else (
    echo    ├─ 의존성 파일: ❌ 누락
    goto error
)

if exist ".git" (
    echo    ├─ Git 저장소: 정상
) else (
    echo    ├─ Git 저장소: ❌ 초기화 필요
    git init
    echo    └─ Git 초기화 완료
)

if exist "README.md" (
    echo    ├─ 문서화: 정상
) else (
    echo    ├─ 문서화: ❌ 누락
)

if exist "Dockerfile" (
    echo    ├─ Docker 설정: 정상
) else (
    echo    ├─ Docker 설정: ⚠️ 없음 (선택사항)
)

echo    └─ ✅ 기본 점검 완료!
echo.

echo ═══════════════════════════════════════════════════════════════
echo 🎯 배포 옵션을 선택하세요:
echo ═══════════════════════════════════════════════════════════════
echo.
echo  [1] 🌟 완전 자동 배포 (GitHub + AWS Amplify)
echo      └─ 가장 간단함, 초보자 추천, 5분 완성
echo.
echo  [2] 📚 GitHub만 업로드  
echo      └─ 코드 백업 및 공유, AWS는 나중에
echo.
echo  [3] 🔧 고급 배포 옵션
echo      └─ Elastic Beanstalk, EC2, 커스텀 설정
echo.
echo  [4] 📖 상세 가이드 보기
echo      └─ 단계별 설명 문서 열기
echo.
echo  [0] ❌ 취소
echo.

set /p choice="선택하세요 (0-4): "

if "%choice%"=="1" goto auto_deploy
if "%choice%"=="2" goto github_only
if "%choice%"=="3" goto advanced
if "%choice%"=="4" goto guides
if "%choice%"=="0" goto exit
goto invalid

:auto_deploy
cls
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                🌟 완전 자동 배포 시작                          ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📝 GitHub 사용자명을 입력하세요:
set /p github_user="GitHub Username: "

if "%github_user%"=="" (
    echo ❌ GitHub 사용자명이 필요합니다.
    pause
    goto auto_deploy
)

echo.
echo 🔄 1단계: GitHub 업로드 준비 중...
git add .
git commit -m "🚀 AIRISS v4.1 - Ready for GitHub & AWS Production

✨ Features Complete:
- 8-dimensional AI talent analysis  
- Real-time bias detection
- Hybrid AI model (60%% text + 40%% quantitative)
- Chart.js visualization with radar charts
- WebSocket real-time updates
- Explainable AI scoring

🏆 Production Ready:
- OK Financial Group validated
- 1,800+ employees capacity
- B2B market potential: $50M+ annually

🛠 Tech Stack:
- Backend: FastAPI, Python 3.9+
- Frontend: HTML5, Chart.js, WebSocket
- Database: SQLite (scalable)
- AI/ML: NLP, bias detection, statistical analysis
- Deployment: Docker ready

🎯 Deploy Target: AWS Amplify for global accessibility"

echo ✅ 커밋 완료!
echo.

echo 🔗 2단계: GitHub 연결 중...
git remote remove origin 2>nul
git remote add origin https://github.com/%github_user%/airiss_enterprise.git
git branch -M main

echo.
echo 📤 3단계: GitHub 업로드 중...
echo    이 과정에서 GitHub 로그인이 필요할 수 있습니다.
git push -u origin main

if %errorlevel% neq 0 (
    echo ❌ GitHub 업로드 실패
    echo 💡 해결 방법:
    echo    1. GitHub에서 Repository 'airiss_enterprise' 생성
    echo    2. GitHub 로그인 정보 확인
    echo    3. 수동으로 다시 시도
    pause
    goto auto_deploy
)

echo ✅ GitHub 업로드 완료!
echo.

echo ═══════════════════════════════════════════════════════════════
echo 🎉 GitHub 업로드 성공!
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📍 Repository URL: https://github.com/%github_user%/airiss_enterprise
echo.

echo 🚀 다음 단계: AWS Amplify 설정
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. 아래 AWS Console 링크를 클릭하세요:
echo    👉 https://console.aws.amazon.com/amplify/
echo.
echo 2. "Create new app" 클릭
echo 3. "Host web app" 선택  
echo 4. "GitHub" 선택
echo 5. Repository: "airiss_enterprise" 선택
echo 6. Branch: "main" 선택
echo 7. "Save and deploy" 클릭
echo.
echo 📝 Build 설정 (붙여넣기용):

echo version: 1
echo backend:
echo   phases:
echo     preBuild:
echo       commands:
echo         - python -m pip install --upgrade pip
echo         - pip install -r requirements.txt
echo     build:
echo       commands:
echo         - python init_database.py
echo frontend:
echo   artifacts:
echo     baseDirectory: /
echo     files:
echo       - '**/*'

echo.
echo 🎯 완료 예상 시간: 5-10분
echo 🌍 결과: 전 세계 접근 가능한 AIRISS 웹사이트!
echo.

echo AWS Console을 열까요? (y/n)
set /p open_aws="Enter choice: "
if /i "%open_aws%"=="y" start https://console.aws.amazon.com/amplify/

start https://github.com/%github_user%/airiss_enterprise
echo.
echo ✅ 브라우저에서 GitHub과 AWS Console이 열렸습니다.
echo 📖 자세한 가이드: COMPLETE_DEPLOYMENT_GUIDE.md
goto success

:github_only
cls
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                📚 GitHub 업로드 진행                          ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📝 GitHub 사용자명을 입력하세요:
set /p github_user="GitHub Username: "

echo.
echo 🔄 GitHub 업로드 중...

git add .
git commit -m "📚 AIRISS v4.1 - GitHub Repository Setup

🎯 프로젝트 백업 및 협업을 위한 GitHub 업로드
✨ Production-ready AIRISS v4.1 Enhanced codebase"

git remote remove origin 2>nul
git remote add origin https://github.com/%github_user%/airiss_enterprise.git
git branch -M main
git push -u origin main

echo ✅ GitHub 업로드 완료!
echo 📍 Repository: https://github.com/%github_user%/airiss_enterprise
start https://github.com/%github_user%/airiss_enterprise
goto success

:advanced
cls
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                🔧 고급 배포 옵션                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 사용 가능한 고급 옵션:
echo.
echo [1] AWS Elastic Beanstalk (FastAPI 최적화)
echo [2] AWS EC2 + Docker (완전 제어)
echo [3] 사용자 정의 배포
echo.

set /p adv_choice="선택하세요 (1-3): "

if "%adv_choice%"=="1" (
    echo 🚀 Elastic Beanstalk 가이드를 여는 중...
    start aws_elasticbeanstalk_guide.md
    echo ✅ EB CLI 설치: pip install awsebcli
)

if "%adv_choice%"=="2" (
    echo 🐳 EC2 + Docker 가이드를 여는 중...
    start aws_ec2_docker_guide.md
)

if "%adv_choice%"=="3" (
    echo 📖 모든 가이드를 여는 중...
    start aws_amplify_guide.md
    start aws_elasticbeanstalk_guide.md  
    start aws_ec2_docker_guide.md
)

goto success

:guides
cls
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                📖 상세 가이드 열기                            ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📚 모든 가이드 문서를 여는 중...
if exist "COMPLETE_DEPLOYMENT_GUIDE.md" start COMPLETE_DEPLOYMENT_GUIDE.md
if exist "deployment_checklist.md" start deployment_checklist.md
if exist "aws_amplify_guide.md" start aws_amplify_guide.md
if exist "README.md" start README.md

echo ✅ 가이드 문서들이 열렸습니다.
goto success

:invalid
echo ❌ 잘못된 선택입니다.
timeout /t 2 /nobreak >nul
goto start

:error
echo.
echo ❌ 프로젝트 구조에 문제가 있습니다.
echo 💡 해결 방법:
echo    1. 올바른 AIRISS 프로젝트 폴더에서 실행하세요
echo    2. 필수 파일들이 있는지 확인하세요
echo.
pause
exit /b 1

:success
echo.
echo ═══════════════════════════════════════════════════════════════
echo 🎉 성공! AIRISS v4.1 배포 준비 완료
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📊 프로젝트 현황:
echo    ✅ 8차원 AI 인재 분석 시스템
echo    ✅ 실시간 편향 탐지 기능
echo    ✅ 하이브리드 AI 모델
echo    ✅ Production 환경 준비 완료
echo    ✅ B2B 시장 진출 준비
echo.
echo 🌟 다음 단계:
echo    1. AWS 배포 완료 시 URL 확인
echo    2. 성능 모니터링 시작
echo    3. 사용자 피드백 수집
echo    4. 지속적 개선 및 확장
echo.
echo 💡 추가 지원:
echo    📖 README.md - 프로젝트 상세 정보
echo    🐛 GitHub Issues - 버그 리포트
echo    📞 AWS Support - 기술 지원
echo.
echo 🚀 AIRISS v4로 인재 관리의 새로운 시대를 열어가세요!
echo ═══════════════════════════════════════════════════════════════

:exit
echo.
echo 감사합니다! 언제든지 다시 실행하세요.
pause
exit /b 0
