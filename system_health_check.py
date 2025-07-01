#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4 시스템 상태 종합 진단 스크립트
작성일: 2025.01.27
목적: 현재 시스템의 모든 구성요소가 정상 작동하는지 확인
"""

import asyncio
import aiohttp
import os
import sys
import json
from datetime import datetime
import subprocess
import psutil
from typing import Dict, List, Tuple

# 색상 코드 정의 (Windows 콘솔 지원)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """헤더 출력"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")

def print_status(component: str, status: str, details: str = ""):
    """상태 출력"""
    if status == "정상":
        color = Colors.OKGREEN
        symbol = "✅"
    elif status == "경고":
        color = Colors.WARNING
        symbol = "⚠️"
    else:
        color = Colors.FAIL
        symbol = "❌"
    
    print(f"{color}{symbol} {component:30} : {status:10}{Colors.ENDC} {details}")

async def check_server_status(host: str = "localhost", port: int = 8002) -> Tuple[bool, str]:
    """서버 상태 확인"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:{port}/health", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return True, f"v{data.get('version', 'unknown')}"
                return False, f"HTTP {resp.status}"
    except Exception as e:
        return False, str(e)

async def check_api_endpoints(host: str = "localhost", port: int = 8002) -> Dict[str, bool]:
    """주요 API 엔드포인트 확인"""
    endpoints = {
        "/api": "API 정보",
        "/health": "헬스체크",
        "/health/db": "DB 상태",
        "/health/analysis": "분석 엔진",
        "/": "메인 UI",
        "/dashboard": "대시보드"
    }
    
    results = {}
    async with aiohttp.ClientSession() as session:
        for endpoint, desc in endpoints.items():
            try:
                async with session.get(f"http://{host}:{port}{endpoint}", timeout=5) as resp:
                    results[endpoint] = resp.status == 200
            except:
                results[endpoint] = False
    
    return results

def check_python_environment() -> Dict[str, str]:
    """Python 환경 확인"""
    import platform
    
    return {
        "Python 버전": sys.version.split()[0],
        "플랫폼": platform.platform(),
        "가상환경": "활성화" if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else "비활성화"
    }

def check_required_packages() -> Dict[str, bool]:
    """필수 패키지 확인"""
    packages = {
        "fastapi": "FastAPI 웹 프레임워크",
        "uvicorn": "ASGI 서버",
        "pandas": "데이터 분석",
        "numpy": "수치 계산",
        "sqlalchemy": "ORM",
        "aiosqlite": "비동기 SQLite",
        "websockets": "WebSocket",
        "openpyxl": "Excel 처리",
        "scikit-learn": "머신러닝"
    }
    
    results = {}
    for pkg, desc in packages.items():
        try:
            __import__(pkg)
            results[pkg] = True
        except ImportError:
            results[pkg] = False
    
    return results

def check_file_structure() -> Dict[str, bool]:
    """프로젝트 파일 구조 확인"""
    required_files = [
        "app/main.py",
        "app/services/text_analyzer.py",
        "app/services/quantitative_analyzer.py",
        "app/services/hybrid_analyzer.py",
        "app/db/sqlite_service.py",
        "app/api/analysis.py",
        "app/api/upload.py",
        "app/templates/index.html",
        "requirements.txt",
        ".env"
    ]
    
    results = {}
    for file_path in required_files:
        results[file_path] = os.path.exists(file_path)
    
    return results

def check_database() -> Tuple[bool, str]:
    """데이터베이스 파일 확인"""
    db_path = "airiss.db"
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        return True, f"{size_mb:.2f} MB"
    return False, "파일 없음"

def check_ports() -> Dict[int, str]:
    """포트 사용 현황 확인"""
    ports_to_check = [8002, 8003, 8080]
    results = {}
    
    for conn in psutil.net_connections():
        if conn.laddr.port in ports_to_check and conn.status == 'LISTEN':
            try:
                proc = psutil.Process(conn.pid)
                results[conn.laddr.port] = proc.name()
            except:
                results[conn.laddr.port] = "Unknown"
    
    return results

def check_log_files() -> Dict[str, str]:
    """로그 파일 확인"""
    log_files = ["airiss_v4.log", "logs/app.log", "debug_logs/debug.log"]
    results = {}
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size_kb = os.path.getsize(log_file) / 1024
            results[log_file] = f"{size_kb:.2f} KB"
        else:
            results[log_file] = "없음"
    
    return results

async def main():
    """메인 진단 함수"""
    print_header("AIRISS v4 시스템 종합 진단")
    print(f"진단 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Python 환경 확인
    print_header("1. Python 환경")
    env_info = check_python_environment()
    for key, value in env_info.items():
        print_status(key, "정상", value)
    
    # 2. 필수 패키지 확인
    print_header("2. 필수 패키지")
    packages = check_required_packages()
    missing_packages = []
    for pkg, installed in packages.items():
        if installed:
            print_status(pkg, "정상", "설치됨")
        else:
            print_status(pkg, "오류", "미설치")
            missing_packages.append(pkg)
    
    # 3. 파일 구조 확인
    print_header("3. 프로젝트 파일 구조")
    files = check_file_structure()
    missing_files = []
    for file_path, exists in files.items():
        if exists:
            print_status(file_path, "정상", "존재")
        else:
            print_status(file_path, "오류", "없음")
            missing_files.append(file_path)
    
    # 4. 데이터베이스 확인
    print_header("4. 데이터베이스")
    db_exists, db_info = check_database()
    if db_exists:
        print_status("airiss.db", "정상", db_info)
    else:
        print_status("airiss.db", "오류", db_info)
    
    # 5. 포트 사용 현황
    print_header("5. 포트 사용 현황")
    ports = check_ports()
    for port, process in ports.items():
        print_status(f"Port {port}", "사용중", process)
    
    # 6. 서버 상태 확인
    print_header("6. AIRISS 서버 상태")
    server_running, server_info = await check_server_status()
    if server_running:
        print_status("AIRISS 서버", "정상", server_info)
        
        # API 엔드포인트 확인
        endpoints = await check_api_endpoints()
        for endpoint, status in endpoints.items():
            if status:
                print_status(f"Endpoint {endpoint}", "정상", "응답 OK")
            else:
                print_status(f"Endpoint {endpoint}", "오류", "응답 없음")
    else:
        print_status("AIRISS 서버", "오류", server_info)
    
    # 7. 로그 파일 확인
    print_header("7. 로그 파일")
    logs = check_log_files()
    for log_file, info in logs.items():
        if info != "없음":
            print_status(log_file, "정상", info)
        else:
            print_status(log_file, "경고", info)
    
    # 8. 종합 진단 결과
    print_header("종합 진단 결과")
    
    issues = []
    if missing_packages:
        issues.append(f"미설치 패키지: {', '.join(missing_packages)}")
    if missing_files:
        issues.append(f"누락된 파일: {', '.join(missing_files[:3])}...")
    if not db_exists:
        issues.append("데이터베이스 파일 없음")
    if not server_running:
        issues.append("서버가 실행되지 않음")
    
    if not issues:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ 시스템 상태: 정상{Colors.ENDC}")
        print("모든 구성요소가 정상적으로 작동하고 있습니다.")
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️ 시스템 상태: 문제 발견{Colors.ENDC}")
        print("\n발견된 문제:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\n권장 조치:")
        if missing_packages:
            print("  1. pip install -r requirements.txt 실행")
        if missing_files:
            print("  2. 프로젝트 파일 구조 확인")
        if not db_exists:
            print("  3. python init_database.py 실행")
        if not server_running:
            print("  4. python -m app.main 또는 run_airiss_v4.bat 실행")
    
    print(f"\n진단 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Windows 환경에서 색상 출력 활성화
    if sys.platform == "win32":
        os.system("color")
    
    asyncio.run(main())
