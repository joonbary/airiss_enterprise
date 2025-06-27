# AIRISS v4.1 Enhanced 시작 스크립트

Write-Host "========================================"
Write-Host " AIRISS v4.1 Enhanced 서버 시작"
Write-Host "========================================"
Write-Host ""

# 현재 디렉토리 저장
$originalPath = Get-Location

# AIRISS 프로젝트 디렉토리로 이동
Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

# Python 환경 확인
Write-Host "Python 환경 확인 중..."
python --version

# 서버 시작
Write-Host ""
Write-Host "AIRISS v4.1 Enhanced 서버를 시작합니다..."
Write-Host ""
Write-Host "접속 주소:"
Write-Host "- 메인 UI: http://localhost:8002/"
Write-Host "- API 문서: http://localhost:8002/docs"
Write-Host "- 대시보드: http://localhost:8002/dashboard"
Write-Host ""
Write-Host "종료하려면 Ctrl+C를 누르세요."
Write-Host "========================================"
Write-Host ""

# Python 모듈로 실행
python -m app.main

# 원래 디렉토리로 돌아가기
Set-Location $originalPath
