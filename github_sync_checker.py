#!/usr/bin/env python3
"""
AIRISS GitHub 동기화 상태 체크 스크립트
IT 비전문가도 쉽게 사용할 수 있는 진단 도구
"""

import os
import subprocess
import json
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def run_command(command, show_output=True):
    """안전하게 명령어 실행"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4")
        if show_output and result.stdout:
            print(result.stdout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ 명령어 실행 실패: {e}")
        return False, "", str(e)

def check_git_status():
    """Git 상태 확인"""
    print_header("Git 리포지토리 상태 확인")
    
    # 현재 브랜치 확인
    success, branch, _ = run_command("git branch --show-current", False)
    if success:
        print(f"✅ 현재 브랜치: {branch.strip()}")
    
    # 원격 저장소 확인
    success, remote, _ = run_command("git remote -v", False)
    if success:
        print(f"✅ 원격 저장소:")
        print(remote)
    
    # 변경사항 확인
    success, status, _ = run_command("git status --porcelain", False)
    if success:
        if status.strip():
            print(f"⚠️ 커밋되지 않은 변경사항이 {len(status.strip().split())} 개 있습니다:")
            run_command("git status --short")
        else:
            print("✅ 모든 변경사항이 커밋되었습니다")
    
    # 원격과의 차이 확인
    run_command("git fetch origin", False)
    success, diff, _ = run_command("git rev-list --count HEAD..origin/main", False)
    if success and diff.strip().isdigit():
        behind_count = int(diff.strip())
        if behind_count > 0:
            print(f"⚠️ 원격 저장소보다 {behind_count} 커밋 뒤처져 있습니다")
        else:
            print("✅ 원격 저장소와 동기화되어 있습니다")

def check_project_files():
    """프로젝트 파일 상태 확인"""
    print_header("프로젝트 파일 상태 확인")
    
    project_root = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
    
    # 주요 파일들 확인
    important_files = [
        "README.md",
        "requirements.txt",
        "app/main.py",
        "app/services/hybrid_analyzer.py",
        ".env",
        "init_database.py"
    ]
    
    print("📁 주요 파일 존재 여부:")
    for file in important_files:
        file_path = os.path.join(project_root, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file} ({size:,} bytes)")
        else:
            print(f"❌ {file} - 파일 없음")
    
    # 프로젝트 크기 확인
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(project_root):
        # .git, node_modules, venv 제외
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__']]
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
                file_count += 1
            except:
                pass
    
    print(f"📊 프로젝트 통계:")
    print(f"   - 총 파일 수: {file_count:,} 개")
    print(f"   - 총 크기: {total_size / 1024 / 1024:.1f} MB")

def check_github_connectivity():
    """GitHub 연결 상태 확인"""
    print_header("GitHub 연결 상태 확인")
    
    # Git 원격 연결 테스트
    success, _, error = run_command("git ls-remote --heads origin", False)
    if success:
        print("✅ GitHub 리포지토리에 정상 연결됨")
    else:
        print(f"❌ GitHub 연결 실패: {error}")
    
    # 마지막 커밋 정보
    success, commit, _ = run_command("git log -1 --oneline", False)
    if success:
        print(f"📝 마지막 로컬 커밋: {commit.strip()}")
    
    # 원격 마지막 커밋
    success, remote_commit, _ = run_command("git log origin/main -1 --oneline", False)
    if success:
        print(f"📝 원격 마지막 커밋: {remote_commit.strip()}")

def generate_sync_report():
    """동기화 보고서 생성"""
    print_header("동기화 보고서 생성")
    
    # 현재 시간
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 로컬 변경사항 수집
    success, status, _ = run_command("git status --porcelain", False)
    changed_files = []
    if success and status.strip():
        changed_files = [line.strip() for line in status.strip().split('\n')]
    
    # 커밋되지 않은 변경사항
    success, diff_stats, _ = run_command("git diff --stat", False)
    
    report = {
        "timestamp": now,
        "local_version": "v4.1",
        "github_version": "v3.0",
        "sync_status": "NEEDS_UPDATE",
        "changed_files_count": len(changed_files),
        "changed_files": changed_files[:10],  # 최대 10개만
        "recommendations": [
            "1. 변경사항을 커밋하세요",
            "2. GitHub에 푸시하세요",
            "3. README.md를 최신 버전으로 업데이트하세요"
        ]
    }
    
    # 보고서 저장
    report_file = os.path.join(r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4", "sync_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 보고서가 저장되었습니다: {report_file}")
    print("\n📋 권장사항:")
    for rec in report["recommendations"]:
        print(f"   {rec}")

def main():
    """메인 실행 함수"""
    print("🚀 AIRISS GitHub 동기화 상태 진단을 시작합니다...")
    print(f"📅 검사 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        check_git_status()
        check_project_files()
        check_github_connectivity()
        generate_sync_report()
        
        print_header("진단 완료")
        print("✅ 모든 진단이 완료되었습니다!")
        print("📄 sync_report.json 파일을 확인하여 상세 내용을 검토하세요.")
        print("\n다음 단계: github_sync_updater.py 실행")
        
    except Exception as e:
        print(f"❌ 진단 중 오류 발생: {e}")
    
    input("\n진단이 완료되었습니다. 엔터 키를 눌러 종료하세요...")

if __name__ == "__main__":
    main()
