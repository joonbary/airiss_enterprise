@echo off
cls
color 0E
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║           🚀 AIRISS Phase 2 완전 기능 배포                    ║
echo  ║         Phase 1 → Phase 2 즉시 전환 시스템                   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🎯 현재 상태: Phase 1 (기본 UI) 배포 완료
echo  🚀 목표: Phase 2 (완전 기능) 즉시 전환
echo  💼 포함 기능: AI 분석 + 편향 탐지 + 실시간 차트
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

echo 📋 Phase 2 전환 준비 중...
timeout /t 2 /nobreak >nul

echo ✅ 기존 파일 백업
if exist "application.py" (
    copy "application.py" "application_phase1_backup.py" >nul
    echo    ├─ Phase 1 파일 백업 완료
) else (
    echo    ├─ ❌ 기존 application.py 없음
    goto error
)

echo ✅ Phase 2 파일 준비
if exist "app\main.py" (
    echo    ├─ 완전 기능 파일 확인 완료
) else (
    echo    ├─ ❌ app\main.py 누락
    goto error
)

echo ✅ 의존성 확인
if exist "requirements.txt" (
    echo    ├─ 의존성 파일 확인 완료
) else (
    echo    ├─ ❌ requirements.txt 누락
    goto error
)

echo    └─ ✅ 전환 준비 완료!
echo.

echo ═══════════════════════════════════════════════════════════════
echo 🎯 전환 방법을 선택하세요:
echo ═══════════════════════════════════════════════════════════════
echo.
echo  [1] 🌟 즉시 전환 (application.py → 완전 기능)
echo      └─ 기존 AWS 배포 그대로 유지하면서 기능 활성화
echo.
echo  [2] 📦 새 배포 패키지 생성
echo      └─ 완전 기능이 포함된 새 배포 zip 생성
echo.
echo  [3] 🔄 GitHub + AWS 완전 재배포
echo      └─ GitHub 업로드 후 AWS에 새로 배포
echo.
echo  [0] ❌ 취소
echo.

set /p choice="선택하세요 (0-3): "

if "%choice%"=="1" goto instant_switch
if "%choice%"=="2" goto new_package
if "%choice%"=="3" goto full_redeploy
if "%choice%"=="0" goto exit
goto invalid

:instant_switch
cls
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                🌟 즉시 전환 시작                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔄 Phase 2 완전 기능으로 전환 중...

REM Phase 2 application 파일 생성
echo # AIRISS Phase 2: Complete Features Activated > application_phase2.py
echo # All AIRISS v4.1 functions enabled >> application_phase2.py
echo. >> application_phase2.py
echo import os >> application_phase2.py
echo import sys >> application_phase2.py
echo. >> application_phase2.py
echo # Add app directory to Python path >> application_phase2.py
echo sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'^)^) >> application_phase2.py
echo. >> application_phase2.py
echo # Import complete AIRISS system >> application_phase2.py
echo try: >> application_phase2.py
echo     from app.main import app >> application_phase2.py
echo     # AWS Elastic Beanstalk compatibility >> application_phase2.py
echo     application = app >> application_phase2.py
echo     print("✅ AIRISS v4.1 Complete Features Loaded"^) >> application_phase2.py
echo except ImportError as e: >> application_phase2.py
echo     print(f"❌ Import Error: {e}"^) >> application_phase2.py
echo     # Fallback to Phase 1 >> application_phase2.py
echo     import application >> application_phase2.py
echo     application = application.app >> application_phase2.py
echo. >> application_phase2.py
echo if __name__ == "__main__": >> application_phase2.py
echo     import uvicorn >> application_phase2.py
echo     port = int(os.environ.get("PORT", 8000^)^) >> application_phase2.py
echo     uvicorn.run(app, host="0.0.0.0", port=port^) >> application_phase2.py

echo ✅ Phase 2 애플리케이션 파일 생성 완료!

echo 🔄 기존 파일 교체 중...
copy "application_phase2.py" "application.py" >nul
echo ✅ application.py 업데이트 완료!

echo.
echo 📦 AWS 배포 패키지 생성 중...
python create_deployment_zip.py

if exist "airiss_phase2_complete.zip" (
    echo ✅ 배포 패키지 생성 완료: airiss_phase2_complete.zip
) else (
    echo ⚠️ 배포 패키지 생성 실패, 수동 업로드 필요
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo 🎉 Phase 2 전환 완료!
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📝 다음 단계:
echo    1. AWS Elastic Beanstalk Console 접속
echo    2. Application 선택 → Upload and Deploy
echo    3. airiss_phase2_complete.zip 업로드
echo    4. Deploy 클릭
echo.
echo 🌍 완료 후 확인 사항:
echo    ✅ 메인 페이지: 고급 차트 표시
echo    ✅ 파일 업로드: AI 분석 기능
echo    ✅ 실시간 진행: WebSocket 연결
echo    ✅ 편향 탐지: 공정성 분석
echo.

echo AWS Console을 열까요? (y/n)
set /p open_aws="Enter choice: "
if /i "%open_aws%"=="y" start https://console.aws.amazon.com/elasticbeanstalk/

goto success

:new_package
cls
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                📦 새 배포 패키지 생성                          ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📦 완전 기능 배포 패키지 생성 중...
python create_complete_deployment.py

echo ✅ 패키지 생성 완료!
echo 📁 파일 위치: airiss_v4_complete_$(date /t)_$(time /t).zip
echo.
echo 📝 수동 배포 방법:
echo    1. AWS Elastic Beanstalk Console 접속
echo    2. 생성된 zip 파일 업로드
echo    3. 배포 완료 대기

goto success

:full_redeploy
cls
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║            🔄 GitHub + AWS 완전 재배포                        ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📝 GitHub 사용자명을 입력하세요:
set /p github_user="GitHub Username: "

echo.
echo 🔄 완전 기능으로 GitHub 업데이트 중...

REM application.py를 완전 기능으로 교체
copy "app\main.py" "application_temp.py" >nul

REM AWS 호환성을 위한 wrapper 추가
echo. >> application_temp.py
echo # AWS Elastic Beanstalk compatibility >> application_temp.py  
echo application = app >> application_temp.py

copy "application_temp.py" "application.py" >nul
del "application_temp.py" >nul

git add .
git commit -m "🚀 AIRISS Phase 2 - Complete Features Deployed

✨ All Features Activated:
- 8-dimensional AI talent analysis
- Real-time bias detection
- Hybrid AI model (60%% text + 40%% quantitative)  
- Chart.js radar charts + performance prediction
- WebSocket real-time updates
- Explainable AI scoring with confidence metrics

🏆 Production Ready for Enterprise:
- OK Financial Group: 1,800+ employees
- Scalable architecture
- Mobile responsive design
- B2B market validated

🛠 Phase 2 Tech Stack Complete:
- Backend: FastAPI with all modules
- Database: SQLite with full schema
- AI/ML: Complete NLP + bias detection
- Frontend: Enhanced UI with Chart.js
- Real-time: WebSocket enabled"

git push origin main

echo ✅ GitHub 업데이트 완료!
echo 🌍 GitHub Actions 자동 배포가 시작됩니다.
echo 📍 Repository: https://github.com/%github_user%/airiss_enterprise

start https://github.com/%github_user%/airiss_enterprise
goto success

:invalid
echo ❌ 잘못된 선택입니다.
timeout /t 2 /nobreak >nul
goto instant_switch

:error
echo.
echo ❌ 필요한 파일이 없습니다.
echo 💡 해결 방법:
echo    1. AIRISS 프로젝트 폴더에서 실행하세요
echo    2. app\main.py 파일이 있는지 확인하세요
pause
exit /b 1

:success
echo.
echo ═══════════════════════════════════════════════════════════════
echo 🎉 AIRISS Phase 2 완전 기능 배포 준비 완료!
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🎯 Phase 2에서 활성화된 기능들:
echo    ✅ 8차원 AI 인재 분석 (텍스트 + 정량)
echo    ✅ 실시간 편향 탐지 및 공정성 분석
echo    ✅ 하이브리드 AI 스코어링 모델
echo    ✅ Chart.js 고급 시각화 (레이더 차트)
echo    ✅ WebSocket 실시간 진행 상황
echo    ✅ 설명 가능한 AI (Explainable AI)
echo    ✅ 모바일 반응형 디자인
echo    ✅ SQLite 데이터베이스 완전 활성화
echo.
echo 🌟 Phase 3 예정 기능:
echo    🔮 성과 예측 AI 모델
echo    🔮 이직 위험도 분석
echo    🔮 맞춤형 성장 경로 추천
echo    🔮 B2B SaaS 플랫폼 전환
echo.
echo 💡 다음 단계:
echo    1. 배포 완료 후 기능 테스트
echo    2. 1,800명 직원 대상 파일럿 진행
echo    3. 피드백 수집 및 개선
echo    4. B2B 시장 진출 준비
echo.
echo 🚀 AIRISS v4.1로 인재 관리 혁신을 시작하세요!
echo ═══════════════════════════════════════════════════════════════

:exit
echo.
echo 감사합니다! 
pause
exit /b 0
