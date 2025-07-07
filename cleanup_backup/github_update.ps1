# AIRISS GitHub 업데이트 스크립트 (PowerShell)
# 우클릭 → "PowerShell로 실행" 하세요

# 콘솔 한글 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🚀 AIRISS GitHub 안전 업데이트" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan
Write-Host ""

# 현재 위치 확인
$projectPath = "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "📁 프로젝트 폴더 확인 중..." -ForegroundColor Yellow

if (Test-Path $projectPath) {
    Set-Location $projectPath
    Write-Host "✅ 프로젝트 폴더 찾음: $projectPath" -ForegroundColor Green
} else {
    Write-Host "❌ 프로젝트 폴더를 찾을 수 없습니다: $projectPath" -ForegroundColor Red
    Write-Host "📁 현재 위치에서 진행합니다: $(Get-Location)" -ForegroundColor Yellow
}

Write-Host ""

# Git 설치 확인
Write-Host "🔍 Git 설치 확인 중..." -ForegroundColor Yellow

try {
    $gitVersion = git --version 2>$null
    if ($gitVersion) {
        Write-Host "✅ Git 설치됨: $gitVersion" -ForegroundColor Green
    } else {
        throw "Git not found"
    }
} catch {
    Write-Host "❌ Git이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "🔗 Git 다운로드: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "엔터 키를 눌러 종료하세요"
    exit 1
}

Write-Host ""

# Git 상태 확인
Write-Host "📊 Git 저장소 상태 확인 중..." -ForegroundColor Yellow

try {
    $gitStatus = git status --porcelain 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Git 저장소가 아닙니다. 초기화가 필요합니다." -ForegroundColor Red
        Read-Host "엔터 키를 눌러 종료하세요"
        exit 1
    }
    
    $changedFiles = ($gitStatus | Measure-Object).Count
    if ($changedFiles -gt 0) {
        Write-Host "📝 변경된 파일 $changedFiles 개 발견" -ForegroundColor Yellow
        Write-Host "변경 내용:" -ForegroundColor Gray
        git status --short
    } else {
        Write-Host "✅ 변경사항 없음 (이미 최신 상태일 수 있음)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Git 상태 확인 실패: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "엔터 키를 눌러 종료하세요"
    exit 1
}

Write-Host ""

# 사용자 확인
$confirmation = Read-Host "GitHub에 업데이트를 진행하시겠습니까? (y/N)"

if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "❌ 업데이트가 취소되었습니다." -ForegroundColor Red
    Read-Host "엔터 키를 눌러 종료하세요"
    exit 0
}

Write-Host ""
Write-Host "🚀 GitHub 업데이트를 시작합니다..." -ForegroundColor Cyan

# 1단계: Git 사용자 설정 (필요한 경우)
Write-Host "⚙️ Git 사용자 설정 확인 중..." -ForegroundColor Yellow

try {
    $userName = git config user.name 2>$null
    $userEmail = git config user.email 2>$null
    
    if (-not $userName) {
        git config user.name "AIRISS Developer"
        Write-Host "✅ Git 사용자 이름 설정 완료" -ForegroundColor Green
    }
    
    if (-not $userEmail) {
        git config user.email "airiss@okfinancialgroup.co.kr"
        Write-Host "✅ Git 사용자 이메일 설정 완료" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Git 사용자 설정 실패 (계속 진행)" -ForegroundColor Yellow
}

# 2단계: 변경사항 스테이징
Write-Host ""
Write-Host "📋 변경사항 스테이징 중..." -ForegroundColor Yellow

try {
    git add . 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 스테이징 완료" -ForegroundColor Green
    } else {
        throw "Staging failed"
    }
} catch {
    Write-Host "❌ 스테이징 실패: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "엔터 키를 눌러 종료하세요"
    exit 1
}

# 3단계: 커밋 생성
Write-Host ""
Write-Host "💾 커밋 생성 중..." -ForegroundColor Yellow

$commitMessage = "Update AIRISS to v4.1 Enhanced - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

try {
    $commitResult = git commit -m $commitMessage 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 커밋 성공: $commitMessage" -ForegroundColor Green
    } elseif ($commitResult -match "nothing to commit") {
        Write-Host "ℹ️ 커밋할 변경사항이 없습니다 (이미 최신 상태)" -ForegroundColor Blue
    } else {
        throw "Commit failed: $commitResult"
    }
} catch {
    Write-Host "❌ 커밋 실패: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "엔터 키를 눌러 종료하세요"
    exit 1
}

# 4단계: 원격 저장소 확인
Write-Host ""
Write-Host "🌐 원격 저장소 연결 확인 중..." -ForegroundColor Yellow

try {
    $remoteUrl = git remote get-url origin 2>$null
    if ($remoteUrl) {
        Write-Host "✅ 원격 저장소: $remoteUrl" -ForegroundColor Green
    } else {
        throw "No remote repository configured"
    }
} catch {
    Write-Host "❌ 원격 저장소 설정 없음" -ForegroundColor Red
    Write-Host "🔧 원격 저장소를 설정합니다..." -ForegroundColor Yellow
    
    try {
        git remote add origin https://github.com/joonbary/airiss_enterprise.git
        Write-Host "✅ 원격 저장소 설정 완료" -ForegroundColor Green
    } catch {
        Write-Host "❌ 원격 저장소 설정 실패" -ForegroundColor Red
        Read-Host "엔터 키를 눌러 종료하세요"
        exit 1
    }
}

# 5단계: GitHub에 푸시
Write-Host ""
Write-Host "🚀 GitHub에 업로드 중..." -ForegroundColor Yellow

try {
    $pushResult = git push origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GitHub 업로드 성공!" -ForegroundColor Green
        Write-Host $pushResult -ForegroundColor Gray
    } else {
        # 브랜치가 master인 경우 시도
        Write-Host "⚠️ main 브랜치 푸시 실패, master 브랜치로 시도..." -ForegroundColor Yellow
        $pushResult = git push origin master 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ GitHub 업로드 성공! (master 브랜치)" -ForegroundColor Green
        } else {
            throw "Push failed: $pushResult"
        }
    }
} catch {
    Write-Host "❌ GitHub 업로드 실패: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 해결 방법:" -ForegroundColor Yellow
    Write-Host "1. 인터넷 연결 확인" -ForegroundColor Gray
    Write-Host "2. GitHub 로그인 상태 확인" -ForegroundColor Gray
    Write-Host "3. 방화벽 설정 확인" -ForegroundColor Gray
    Read-Host "엔터 키를 눌러 종료하세요"
    exit 1
}

# 6단계: 결과 확인
Write-Host ""
Write-Host "🎉 업데이트 완료!" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Green

$githubUrl = "https://github.com/joonbary/airiss_enterprise"
Write-Host "🔗 GitHub 페이지: $githubUrl" -ForegroundColor Cyan

# 브라우저에서 열기 옵션
$openBrowser = Read-Host "GitHub 페이지를 브라우저에서 열까요? (y/N)"
if ($openBrowser -eq 'y' -or $openBrowser -eq 'Y') {
    Start-Process $githubUrl
    Write-Host "✅ 브라우저에서 GitHub 페이지가 열렸습니다." -ForegroundColor Green
}

Write-Host ""
Write-Host "📊 업데이트 요약:" -ForegroundColor Cyan
Write-Host "   🎯 버전: AIRISS v4.1 Enhanced" -ForegroundColor Gray
Write-Host "   📅 시간: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "   ✅ 상태: 성공" -ForegroundColor Gray
Write-Host "   🔗 링크: $githubUrl" -ForegroundColor Gray

Write-Host ""
Write-Host "🎉 축하합니다! AIRISS v4.1이 GitHub에 성공적으로 업로드되었습니다!" -ForegroundColor Green

Read-Host "엔터 키를 눌러 종료하세요"
