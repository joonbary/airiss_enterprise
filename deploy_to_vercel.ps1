# 🚀 AIRISS V4 Vercel 배포 PowerShell 스크립트
Write-Host "🚀 AIRISS V4 Vercel 배포 자동화 스크립트" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 현재 디렉토리 확인
$frontendPath = "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend"
Set-Location $frontendPath
Write-Host "📍 현재 위치: $PWD" -ForegroundColor Yellow

# 1단계: 빌드 테스트
Write-Host ""
Write-Host "🔨 1단계: 빌드 테스트 중..." -ForegroundColor Cyan
try {
    & npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "빌드 실패"
    }
    Write-Host "✅ 빌드 성공!" -ForegroundColor Green
} catch {
    Write-Host "❌ 빌드 실패! 오류를 확인하고 다시 시도하세요." -ForegroundColor Red
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# 2단계: 배포용 디렉토리 생성
Write-Host ""
Write-Host "📁 2단계: 배포용 프로젝트 준비 중..." -ForegroundColor Cyan
$deployDir = "$env:USERPROFILE\Desktop\airiss-frontend-deploy"

if (Test-Path $deployDir) {
    Write-Host "🗑️ 기존 배포 폴더 삭제 중..." -ForegroundColor Yellow
    Remove-Item $deployDir -Recurse -Force
}
New-Item -Path $deployDir -ItemType Directory | Out-Null

# 3단계: 파일 복사
Write-Host "📋 3단계: 필요한 파일들 복사 중..." -ForegroundColor Cyan

# 폴더 복사
Copy-Item "src" "$deployDir\src" -Recurse -Force
Copy-Item "public" "$deployDir\public" -Recurse -Force

# 파일 복사
$filesToCopy = @("package.json", "tsconfig.json", ".env.production", "vercel.json")
foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file $deployDir -Force
    }
}

if (Test-Path "README.md") {
    Copy-Item "README.md" $deployDir -Force
}

# 불필요한 파일 제거
$unnecessaryFiles = @(".env", "node_modules", "package-lock.json")
foreach ($item in $unnecessaryFiles) {
    $itemPath = Join-Path $deployDir $item
    if (Test-Path $itemPath) {
        Remove-Item $itemPath -Recurse -Force
    }
}

Set-Location $deployDir

# 4단계: package.json 최적화
Write-Host "⚙️ 4단계: package.json 최적화 중..." -ForegroundColor Cyan
$packageJson = Get-Content "package.json" | ConvertFrom-Json
$packageJson.private = $false
$packageJson.homepage = "."
$packageJson | ConvertTo-Json -Depth 10 | Set-Content "package.json"

# 5단계: 의존성 설치
Write-Host "📦 5단계: 의존성 설치 중..." -ForegroundColor Cyan
& npm install

# 6단계: 최종 빌드 테스트
Write-Host "🔍 6단계: 최종 빌드 테스트 중..." -ForegroundColor Cyan
try {
    & npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "최종 빌드 실패"
    }
} catch {
    Write-Host "❌ 최종 빌드 실패!" -ForegroundColor Red
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# 7단계: Git 초기화
Write-Host "🐙 7단계: Git 저장소 초기화 중..." -ForegroundColor Cyan
& git init
& git add .
& git commit -m "🚀 AIRISS V4 Frontend - Ready for Vercel Deployment"

Write-Host ""
Write-Host "✅ 모든 준비가 완료되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 배포용 파일 위치: $deployDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎯 다음 단계:" -ForegroundColor Cyan
Write-Host "1. GitHub에서 새 저장소 생성: airiss-v4-frontend" -ForegroundColor White
Write-Host "2. 다음 명령어 실행:" -ForegroundColor White
Write-Host "   git branch -M main" -ForegroundColor Gray
Write-Host "   git remote add origin https://github.com/[YOUR-USERNAME]/airiss-v4-frontend.git" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "3. vercel.com에서 GitHub 저장소 연결하여 배포" -ForegroundColor White
Write-Host ""
Write-Host "🌐 배포 후 접속 테스트:" -ForegroundColor Cyan
Write-Host "   - 메인 페이지 로딩 확인" -ForegroundColor White
Write-Host "   - 라우팅 동작 확인 (/dashboard, /upload 등)" -ForegroundColor White
Write-Host "   - 콘솔 에러 없음 확인" -ForegroundColor White
Write-Host ""

Read-Host "완료! Enter를 누르세요"
