#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 실시간 시스템 모니터링 도구
작성일: 2025.01.28
"""

import asyncio
import aiohttp
import psutil
import json
import time
from datetime import datetime
import os
import sys
from typing import Dict, Any, List
import sqlite3

# 색상 코드
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'
    CLEAR = '\033[2J\033[H'  # 화면 지우기

class AIRISSMonitor:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.analysis_count = 0
        self.db_path = "airiss.db"
        
    async def check_server_health(self) -> Dict[str, Any]:
        """서버 상태 확인"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        return await response.json()
        except:
            return {"status": "offline", "error": "서버 연결 실패"}
    
    async def check_api_endpoints(self) -> List[Dict[str, Any]]:
        """주요 API 엔드포인트 상태 확인"""
        endpoints = [
            {"name": "Health", "url": "/health", "method": "GET"},
            {"name": "DB Health", "url": "/health/db", "method": "GET"},
            {"name": "Analysis Health", "url": "/health/analysis", "method": "GET"},
            {"name": "Upload API", "url": "/upload/files/", "method": "GET"},
            {"name": "Analysis API", "url": "/analysis/jobs", "method": "GET"},
            {"name": "API Docs", "url": "/docs", "method": "GET"}
        ]
        
        results = []
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    start = time.time()
                    async with session.request(
                        endpoint["method"], 
                        f"{self.base_url}{endpoint['url']}", 
                        timeout=5
                    ) as response:
                        elapsed = (time.time() - start) * 1000  # ms
                        results.append({
                            "name": endpoint["name"],
                            "url": endpoint["url"],
                            "status": response.status,
                            "response_time": elapsed,
                            "healthy": 200 <= response.status < 300
                        })
                        self.request_count += 1
                except Exception as e:
                    results.append({
                        "name": endpoint["name"],
                        "url": endpoint["url"],
                        "status": 0,
                        "response_time": 0,
                        "healthy": False,
                        "error": str(e)
                    })
                    self.error_count += 1
        
        return results
    
    def check_system_resources(self) -> Dict[str, Any]:
        """시스템 리소스 확인"""
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        
        # 프로세스 정보
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'memory': proc.info['memory_percent'],
                        'cpu': proc.info['cpu_percent']
                    })
            except:
                pass
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count()
            },
            "memory": {
                "percent": memory.percent,
                "used_gb": memory.used / (1024**3),
                "total_gb": memory.total / (1024**3)
            },
            "disk": {
                "percent": disk.percent,
                "used_gb": disk.used / (1024**3),
                "total_gb": disk.total / (1024**3)
            },
            "python_processes": python_processes[:3]  # 상위 3개만
        }
    
    def check_database_stats(self) -> Dict[str, Any]:
        """데이터베이스 통계"""
        stats = {
            "exists": os.path.exists(self.db_path),
            "size_mb": 0,
            "tables": {},
            "total_records": 0
        }
        
        if stats["exists"]:
            stats["size_mb"] = os.path.getsize(self.db_path) / (1024**2)
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 테이블별 레코드 수
                tables = ['files', 'analyses', 'analysis_results']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats["tables"][table] = count
                        stats["total_records"] += count
                    except:
                        stats["tables"][table] = 0
                
                conn.close()
            except:
                pass
        
        return stats
    
    def format_uptime(self) -> str:
        """가동 시간 포맷"""
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def print_dashboard(self, data: Dict[str, Any]):
        """대시보드 출력"""
        # 화면 지우기
        print(Colors.CLEAR, end='')
        
        # 헤더
        print(f"{Colors.BOLD}{Colors.BLUE}╔═══════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}║          AIRISS v4.0 실시간 시스템 모니터링 대시보드                  ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}╚═══════════════════════════════════════════════════════════════════════╝{Colors.END}\n")
        
        # 시간 정보
        print(f"{Colors.CYAN}📅 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  가동 시간: {self.format_uptime()}{Colors.END}\n")
        
        # 서버 상태
        server_health = data.get('server_health', {})
        status = server_health.get('status', 'unknown')
        if status == 'healthy':
            status_color = Colors.GREEN
            status_icon = "✅"
        else:
            status_color = Colors.RED
            status_icon = "❌"
        
        print(f"{Colors.BOLD}[서버 상태]{Colors.END}")
        print(f"{status_icon} 상태: {status_color}{status.upper()}{Colors.END}")
        if status == 'healthy':
            print(f"   버전: {server_health.get('version', 'N/A')}")
            print(f"   시작: {server_health.get('timestamp', 'N/A')}")
        print()
        
        # API 엔드포인트 상태
        print(f"{Colors.BOLD}[API 엔드포인트 상태]{Colors.END}")
        endpoints = data.get('endpoints', [])
        for ep in endpoints:
            if ep['healthy']:
                icon = "✅"
                time_color = Colors.GREEN if ep['response_time'] < 100 else Colors.YELLOW
            else:
                icon = "❌"
                time_color = Colors.RED
            
            print(f"{icon} {ep['name']:15} [{ep['status']:3}] {time_color}{ep['response_time']:6.1f}ms{Colors.END}")
        print()
        
        # 시스템 리소스
        print(f"{Colors.BOLD}[시스템 리소스]{Colors.END}")
        resources = data.get('resources', {})
        
        # CPU
        cpu = resources.get('cpu', {})
        cpu_percent = cpu.get('percent', 0)
        cpu_color = Colors.GREEN if cpu_percent < 50 else Colors.YELLOW if cpu_percent < 80 else Colors.RED
        print(f"🖥️  CPU: {cpu_color}{cpu_percent:5.1f}%{Colors.END} ({cpu.get('cores', 0)} cores)")
        
        # 메모리
        memory = resources.get('memory', {})
        mem_percent = memory.get('percent', 0)
        mem_color = Colors.GREEN if mem_percent < 50 else Colors.YELLOW if mem_percent < 80 else Colors.RED
        print(f"💾 메모리: {mem_color}{mem_percent:5.1f}%{Colors.END} ({memory.get('used_gb', 0):.1f}/{memory.get('total_gb', 0):.1f} GB)")
        
        # 디스크
        disk = resources.get('disk', {})
        disk_percent = disk.get('percent', 0)
        disk_color = Colors.GREEN if disk_percent < 70 else Colors.YELLOW if disk_percent < 90 else Colors.RED
        print(f"💿 디스크: {disk_color}{disk_percent:5.1f}%{Colors.END} ({disk.get('used_gb', 0):.1f}/{disk.get('total_gb', 0):.1f} GB)")
        print()
        
        # 데이터베이스 통계
        print(f"{Colors.BOLD}[데이터베이스 통계]{Colors.END}")
        db_stats = data.get('db_stats', {})
        if db_stats.get('exists'):
            print(f"📊 크기: {db_stats.get('size_mb', 0):.2f} MB")
            print(f"📁 테이블별 레코드:")
            for table, count in db_stats.get('tables', {}).items():
                print(f"   - {table}: {count:,} 건")
            print(f"📈 총 레코드: {db_stats.get('total_records', 0):,} 건")
        else:
            print("❌ 데이터베이스 파일 없음")
        print()
        
        # API 통계
        print(f"{Colors.BOLD}[API 통계]{Colors.END}")
        print(f"📤 총 요청: {self.request_count:,} 건")
        print(f"❌ 오류: {self.error_count:,} 건")
        if self.request_count > 0:
            error_rate = (self.error_count / self.request_count) * 100
            error_color = Colors.GREEN if error_rate < 1 else Colors.YELLOW if error_rate < 5 else Colors.RED
            print(f"📊 오류율: {error_color}{error_rate:.2f}%{Colors.END}")
        print()
        
        # Python 프로세스
        print(f"{Colors.BOLD}[Python 프로세스]{Colors.END}")
        py_procs = resources.get('python_processes', [])
        if py_procs:
            for i, proc in enumerate(py_procs[:3], 1):
                print(f"   {i}. PID: {proc['pid']} | CPU: {proc['cpu']:.1f}% | 메모리: {proc['memory']:.1f}%")
        else:
            print("   활성 Python 프로세스 없음")
        
        # 하단 정보
        print(f"\n{Colors.PURPLE}새로고침: 5초 | 종료: Ctrl+C{Colors.END}")
    
    async def monitor_loop(self):
        """모니터링 루프"""
        print("모니터링을 시작합니다...")
        
        while True:
            try:
                # 데이터 수집
                data = {
                    'server_health': await self.check_server_health(),
                    'endpoints': await self.check_api_endpoints(),
                    'resources': self.check_system_resources(),
                    'db_stats': self.check_database_stats()
                }
                
                # 대시보드 출력
                self.print_dashboard(data)
                
                # 5초 대기
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}모니터링을 종료합니다...{Colors.END}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}오류 발생: {e}{Colors.END}")
                await asyncio.sleep(5)

async def main():
    """메인 함수"""
    # Windows 색상 지원
    if sys.platform == "win32":
        os.system("color")
    
    monitor = AIRISSMonitor()
    await monitor.monitor_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
