@echo off
echo ============================================================
echo 🎯 AIRISS v4 프로젝트 정리 스크립트
echo ============================================================
echo.
echo 이 스크립트는 다음을 수행합니다:
echo ✅ 전체 백업 생성 (안전성 보장)
echo 🧹 불필요한 파일들 정리 (백업/임시/중복 파일)
echo 📦 정리된 파일들을 cleanup_backup 폴더로 이동
echo 📋 깔끔한 프로젝트 구조 요약 생성
echo.
echo 정리 후 유지되는 핵심 구조:
echo ├── app/                 (백엔드 API)
echo ├── airiss-v4-frontend/  (React 프론트엔드)  
echo ├── requirements.txt     (의존성)
echo ├── README.md           (문서)
echo ├── Dockerfile          (컨테이너)
echo └── .env.example        (환경설정)
echo.
echo ⚠️  주의: 정리 전 전체 백업이 자동으로 생성됩니다.
echo.
set /p choice="정리를 진행하시겠습니까? (y/N): "

if /i "%choice%"=="y" (
    echo.
    echo 🚀 정리 시작...
    python cleanup_airiss_v4.py
    echo.
    echo ✅ 정리 완료! 
    echo 📋 PROJECT_STRUCTURE_CLEAN.md 파일을 확인하세요.
    echo 📦 backup 폴더에서 백업 파일들을 확인할 수 있습니다.
) else (
    echo.
    echo ❌ 정리가 취소되었습니다.
)

echo.
pause
