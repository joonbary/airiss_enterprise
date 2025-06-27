@echo off
title Claude 클린 재설치 도우미
echo ===============================
echo Claude 클린 설치를 시작합니다...
echo ===============================

:: 1. Claude 프로세스 종료
echo [1] Claude 관련 프로세스 종료 중...
taskkill /f /im Claude.exe >nul 2>&1
taskkill /f /im electron.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

:: 2. 설정 폴더 삭제
echo [2] 설정 및 캐시 폴더 삭제 중...
rd /s /q "%APPDATA%\Claude"
rd /s /q "%LOCALAPPDATA%\Claude"
rd /s /q "%LOCALAPPDATA%\AnthropicClaude"
rd /s /q "%APPDATA%\AnthropicClaude"

:: 3. 설치 경로 제거 (일반적으로 이 경로는 수동 확인 필요)
echo [3] 기존 설치 경로 제거 시도 중...
set CLAUDE_DIR="%ProgramFiles%\Claude"
if exist %CLAUDE_DIR% (
    rd /s /q %CLAUDE_DIR%
)

:: 4. 완료 메시지
echo.
echo ✅ 클린업이 완료되었습니다.
echo ▶ 수동으로 최신 Claude 설치파일을 다시 실행하세요.
echo.
echo 👉 설치 파일이 없다면 다음 사이트를 참고하세요:
echo     https://www.anthropic.com 또는 내부 배포 링크
echo.
pause
exit
