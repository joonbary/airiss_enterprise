#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 종합 테스트 및 디버깅 스크립트
작성일: 2025.01.28
목적: 전체 시스템 작동 상태 확인 및 문제점 진단
"""

import os
import sys
import json
import time
import pandas as pd
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import subprocess

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('airiss_v4_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 색상 코드
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """헤더 출력"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_status(status, message, detail=None):
    """상태 메시지 출력"""
    if status == "OK":
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
    elif status == "WARNING":
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
    elif status == "ERROR":
        print(f"{Colors.RED}✗{Colors.END} {message}")
    elif status == "INFO":
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")
    else:
        print(f"  {message}")
    
    if detail:
        print(f"   └─ {Colors.PURPLE}{detail}{Colors.END}")

def test_imports():
    """필수 모듈 임포트 테스트"""
    print_header("1. 필수 모듈 임포트 테스트")
    
    required_modules = {
        'fastapi': 'FastAPI 웹 프레임워크',
        'uvicorn': 'ASGI 서버',
        'pandas': '데이터 처리',
        'numpy': '수치 연산',
        'openpyxl': 'Excel 파일 처리',
        'sqlalchemy': '데이터베이스 ORM',
        'scipy': '통계 분석',
        'sklearn': '머신러닝',
        'websockets': 'WebSocket 통신',
        'jinja2': '템플릿 엔진',
        'aiofiles': '비동기 파일 처리',
        'httpx': 'HTTP 클라이언트'
    }
    
    success_count = 0
    failed_modules = []
    
    for module_name, description in required_modules.items():
        try:
            if module_name == 'sklearn':
                __import__('sklearn')
            else:
                __import__(module_name)
            print_status("OK", f"{module_name} - {description}")
            success_count += 1
        except ImportError as e:
            print_status("ERROR", f"{module_name} - {description}", str(e))
            failed_modules.append(module_name)
    
    print(f"\n📊 결과: {success_count}/{len(required_modules)} 모듈 임포트 성공")
    
    if failed_modules:
        print_status("WARNING", "누락된 모듈 설치가 필요합니다:")
        print(f"   pip install {' '.join(failed_modules)}")
    
    return len(failed_modules) == 0

def test_project_structure():
    """프로젝트 구조 확인"""
    print_header("2. 프로젝트 구조 확인")
    
    required_structure = {
        'dirs': [
            ('app', '애플리케이션 메인'),
            ('app/api', 'API 엔드포인트'),
            ('app/services', '핵심 서비스'),
            ('app/templates', 'HTML 템플릿'),
            ('app/static', '정적 파일'),
            ('app/db', '데이터베이스 서비스'),
            ('app/core', '핵심 모듈'),
            ('app/middleware', '미들웨어'),
            ('app/models', '데이터 모델'),
            ('app/schemas', '스키마 정의'),
            ('uploads', '업로드 파일'),
            ('logs', '로그 파일'),
            ('tests', '테스트 코드')
        ],
        'files': [
            ('app/main.py', '메인 애플리케이션'),
            ('app/services/text_analyzer.py', '텍스트 분석기'),
            ('app/services/quantitative_analyzer.py', '정량 분석기'),
            ('app/services/hybrid_analyzer.py', '하이브리드 분석기'),
            ('app/db/sqlite_service.py', 'SQLite 서비스'),
            ('app/core/websocket_manager.py', 'WebSocket 관리자'),
            ('requirements.txt', '패키지 목록'),
            ('.env', '환경 설정')
        ]
    }
    
    all_good = True
    
    # 디렉토리 확인
    print_status("INFO", "디렉토리 구조 확인 중...")
    for dir_path, description in required_structure['dirs']:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print_status("OK", f"{dir_path}/ - {description}")
        else:
            print_status("WARNING", f"{dir_path}/ - {description} (생성 중...)")
            os.makedirs(dir_path, exist_ok=True)
            all_good = False
    
    # 파일 확인
    print_status("INFO", "\n핵심 파일 확인 중...")
    for file_path, description in required_structure['files']:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print_status("OK", f"{file_path} - {description}", f"{size:,} bytes")
        else:
            print_status("ERROR", f"{file_path} - {description} (누락됨)")
            all_good = False
    
    return all_good

async def test_core_services():
    """핵심 서비스 기능 테스트"""
    print_header("3. 핵심 서비스 기능 테스트")
    
    results = {}
    
    # 1. Text Analyzer 테스트
    print_status("INFO", "텍스트 분석기 테스트 중...")
    try:
        from app.services.text_analyzer import AIRISSTextAnalyzer
        analyzer = AIRISSTextAnalyzer()
        
        test_cases = [
            ("우수한 성과를 보여주었습니다", "업무성과", 70),
            ("팀워크가 뛰어나고 협력적입니다", "리더십협업", 70),
            ("개선이 필요한 부분이 있습니다", "태도마인드", 40)
        ]
        
        for text, dimension, expected_min in test_cases:
            result = analyzer.analyze_text(text, dimension)
            if result['score'] >= expected_min:
                print_status("OK", f"  '{text[:20]}...' → {result['score']}점")
            else:
                print_status("WARNING", f"  '{text[:20]}...' → {result['score']}점 (예상: {expected_min}+)")
        
        results['text_analyzer'] = True
        print_status("OK", "텍스트 분석기 정상 작동")
        
    except Exception as e:
        print_status("ERROR", f"텍스트 분석기 오류: {str(e)}")
        results['text_analyzer'] = False
        logger.error(f"Text Analyzer Error: {e}", exc_info=True)
    
    # 2. Quantitative Analyzer 테스트
    print_status("INFO", "\n정량 분석기 테스트 중...")
    try:
        from app.services.quantitative_analyzer import QuantitativeAnalyzer
        analyzer = QuantitativeAnalyzer()
        
        test_data = pd.Series({
            'KPI달성률': 90,
            '출근율': 95,
            '평가등급': 'A',
            '교육이수시간': 40,
            '프로젝트성과': 85
        })
        
        quant_data = analyzer.extract_quantitative_data(test_data)
        result = analyzer.calculate_quantitative_score(quant_data)
        
        print_status("OK", f"  정량 점수: {result['quantitative_score']}점")
        print_status("INFO", f"  데이터 품질: {result['data_quality']}")
        print_status("INFO", f"  신뢰도: {result['confidence']}%")
        
        results['quant_analyzer'] = True
        print_status("OK", "정량 분석기 정상 작동")
        
    except Exception as e:
        print_status("ERROR", f"정량 분석기 오류: {str(e)}")
        results['quant_analyzer'] = False
        logger.error(f"Quantitative Analyzer Error: {e}", exc_info=True)
    
    # 3. Hybrid Analyzer 테스트
    print_status("INFO", "\n하이브리드 분석기 테스트 중...")
    try:
        from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
        analyzer = AIRISSHybridAnalyzer()
        
        test_row = pd.Series({
            'uid': 'TEST001',
            'opinion': '성실하게 업무를 수행하고 있으며, 팀과의 협업도 원활합니다.',
            'KPI달성률': 85,
            '출근율': 98,
            '평가등급': 'B+'
        })
        
        result = analyzer.comprehensive_analysis(
            'TEST001', 
            test_row['opinion'], 
            test_row
        )
        
        hybrid_score = result['hybrid_analysis']['overall_score']
        grade = result['hybrid_analysis']['grade']
        
        print_status("OK", f"  하이브리드 점수: {hybrid_score}점")
        print_status("INFO", f"  등급: {grade}")
        print_status("INFO", f"  텍스트 기여도: {result['hybrid_analysis']['analysis_composition']['text_weight']}%")
        print_status("INFO", f"  정량 기여도: {result['hybrid_analysis']['analysis_composition']['quantitative_weight']}%")
        
        results['hybrid_analyzer'] = True
        print_status("OK", "하이브리드 분석기 정상 작동")
        
    except Exception as e:
        print_status("ERROR", f"하이브리드 분석기 오류: {str(e)}")
        results['hybrid_analyzer'] = False
        logger.error(f"Hybrid Analyzer Error: {e}", exc_info=True)
    
    # 4. SQLite Service 테스트
    print_status("INFO", "\nSQLite 서비스 테스트 중...")
    try:
        from app.db.sqlite_service import SQLiteService
        service = SQLiteService()
        await service.init_database()
        
        # 테이블 확인
        tables = await service.get_all_tables()
        print_status("INFO", f"  테이블 수: {len(tables)}")
        for table in tables[:5]:  # 처음 5개만 표시
            print_status("OK", f"  - {table}")
        
        results['sqlite_service'] = True
        print_status("OK", "SQLite 서비스 정상 작동")
        
    except Exception as e:
        print_status("ERROR", f"SQLite 서비스 오류: {str(e)}")
        results['sqlite_service'] = False
        logger.error(f"SQLite Service Error: {e}", exc_info=True)
    
    # 5. WebSocket Manager 테스트
    print_status("INFO", "\nWebSocket 관리자 테스트 중...")
    try:
        from app.core.websocket_manager import ConnectionManager
        manager = ConnectionManager()
        
        # 기본 기능 확인
        print_status("OK", "  WebSocket 관리자 초기화 성공")
        print_status("INFO", f"  활성 연결 수: {len(manager.active_connections)}")
        
        results['websocket_manager'] = True
        print_status("OK", "WebSocket 관리자 정상 작동")
        
    except Exception as e:
        print_status("ERROR", f"WebSocket 관리자 오류: {str(e)}")
        results['websocket_manager'] = False
        logger.error(f"WebSocket Manager Error: {e}", exc_info=True)
    
    return results

def test_database():
    """데이터베이스 상태 확인"""
    print_header("4. 데이터베이스 상태 확인")
    
    db_file = "airiss.db"
    
    if not os.path.exists(db_file):
        print_status("WARNING", f"{db_file} 파일이 없습니다. 새로 생성됩니다.")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 파일 크기
        size_mb = os.path.getsize(db_file) / 1024 / 1024
        print_status("OK", f"데이터베이스 파일 크기: {size_mb:.2f} MB")
        
        # 테이블 목록
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print_status("INFO", f"테이블 수: {len(tables)}")
        
        # 주요 테이블 레코드 수 확인
        important_tables = ['files', 'analyses', 'analysis_results']
        for table_name in important_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print_status("OK", f"  {table_name}: {count:,} 레코드")
            except:
                print_status("WARNING", f"  {table_name}: 테이블 없음")
        
        conn.close()
        return True
        
    except Exception as e:
        print_status("ERROR", f"데이터베이스 연결 실패: {str(e)}")
        return False

def test_server_running():
    """서버 실행 상태 확인"""
    print_header("5. 서버 실행 상태 확인")
    
    import urllib.request
    import urllib.error
    
    base_url = "http://localhost:8002"
    
    try:
        with urllib.request.urlopen(f"{base_url}/health", timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                print_status("OK", f"서버가 실행 중입니다 (포트: 8002)")
                print_status("INFO", f"  상태: {data.get('status', 'unknown')}")
                print_status("INFO", f"  시간: {data.get('timestamp', 'unknown')}")
                return True
    except urllib.error.URLError:
        print_status("ERROR", "서버가 실행되지 않았습니다")
        print_status("INFO", "서버 시작 명령:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload")
        print("   또는")
        print("   AIRISS_OneClick.bat")
        return False
    except Exception as e:
        print_status("ERROR", f"서버 확인 중 오류: {str(e)}")
        return False

def generate_test_data():
    """테스트 데이터 생성"""
    print_header("6. 테스트 데이터 생성")
    
    try:
        test_data = pd.DataFrame({
            'uid': ['TEST001', 'TEST002', 'TEST003', 'TEST004', 'TEST005'],
            'name': ['김철수', '이영희', '박민수', '최지은', '정대호'],
            'department': ['영업부', '기획부', '개발부', '인사부', '재무부'],
            'position': ['과장', '대리', '차장', '사원', '부장'],
            'opinion': [
                '매우 우수한 성과를 보여주었으며, 팀워크도 훌륭합니다. 리더십이 뛰어나고 창의적입니다.',
                '성실하게 업무를 수행하고 있으나, 커뮤니케이션 부분에서 개선이 필요합니다.',
                '기술적 전문성이 뛰어나며, 문제 해결 능력이 탁월합니다. 혁신적인 아이디어를 제시합니다.',
                '학습 의지가 높고 조직 적응력이 좋습니다. 더 많은 경험이 필요한 단계입니다.',
                '안정적인 업무 처리와 높은 신뢰도를 보입니다. 변화에 대한 적응력을 높일 필요가 있습니다.'
            ],
            'KPI달성률': [95, 75, 88, 70, 82],
            '출근율': [98, 92, 96, 99, 94],
            '평가등급': ['A', 'B', 'A', 'C', 'B+'],
            '교육이수시간': [45, 20, 60, 35, 25],
            '프로젝트성과': [90, 70, 85, 65, 80]
        })
        
        # 파일 저장
        filename = f'test_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        test_data.to_excel(filename, index=False)
        
        print_status("OK", f"테스트 데이터 생성 완료: {filename}")
        print_status("INFO", f"  레코드 수: {len(test_data)}")
        print_status("INFO", f"  컬럼 수: {len(test_data.columns)}")
        
        # 데이터 미리보기
        print("\n📊 데이터 미리보기:")
        print(test_data[['uid', 'name', 'KPI달성률', '평가등급']].to_string(index=False))
        
        return True, filename
        
    except Exception as e:
        print_status("ERROR", f"테스트 데이터 생성 실패: {str(e)}")
        return False, None

def generate_diagnosis_report(test_results):
    """종합 진단 보고서 생성"""
    print_header("7. 종합 진단 보고서")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'system_version': 'AIRISS v4.0',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': sys.platform,
        'test_results': test_results,
        'recommendations': []
    }
    
    # 전체 상태 평가
    all_passed = all([
        test_results.get('imports_ok', False),
        test_results.get('structure_ok', False),
        test_results.get('database_ok', False),
        test_results.get('services', {}).get('text_analyzer', False),
        test_results.get('services', {}).get('quant_analyzer', False),
        test_results.get('services', {}).get('hybrid_analyzer', False)
    ])
    
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ 시스템 상태: 정상{Colors.END}")
        print("모든 핵심 구성 요소가 정상 작동합니다.")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ 시스템 상태: 일부 문제 발견{Colors.END}")
        
        # 권장사항 생성
        if not test_results.get('imports_ok'):
            report['recommendations'].append("필수 패키지를 설치하세요: pip install -r requirements.txt")
        
        if not test_results.get('structure_ok'):
            report['recommendations'].append("프로젝트 구조를 점검하고 누락된 파일을 복구하세요")
        
        if not test_results.get('database_ok'):
            report['recommendations'].append("데이터베이스를 초기화하세요: python init_database.py")
        
        services = test_results.get('services', {})
        if not all([services.get('text_analyzer'), services.get('quant_analyzer'), services.get('hybrid_analyzer')]):
            report['recommendations'].append("분석 서비스 모듈을 점검하세요")
    
    # 보고서 저장
    report_filename = f'diagnosis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_status("OK", f"\n진단 보고서 저장: {report_filename}")
    
    if report['recommendations']:
        print("\n📌 권장 조치사항:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    return report

async def main():
    """메인 테스트 함수"""
    print(Colors.BOLD + Colors.BLUE + """
    ╔═══════════════════════════════════════════════════════════════╗
    ║         AIRISS v4.0 종합 테스트 및 디버깅 도구               ║
    ║     AI-based Resource Intelligence Scoring System              ║
    ║                                                               ║
    ║     작성일: 2025.01.28  |  버전: 4.0                          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """ + Colors.END)
    
    test_results = {}
    
    # 1. 모듈 임포트 테스트
    test_results['imports_ok'] = test_imports()
    
    # 2. 프로젝트 구조 확인
    test_results['structure_ok'] = test_project_structure()
    
    # 3. 핵심 서비스 테스트
    test_results['services'] = await test_core_services()
    
    # 4. 데이터베이스 확인
    test_results['database_ok'] = test_database()
    
    # 5. 서버 실행 상태 확인
    test_results['server_running'] = test_server_running()
    
    # 6. 테스트 데이터 생성
    data_created, data_file = generate_test_data()
    test_results['test_data_created'] = data_created
    test_results['test_data_file'] = data_file
    
    # 7. 종합 진단 보고서
    report = generate_diagnosis_report(test_results)
    
    # 최종 안내
    print("\n" + "="*70)
    print(f"{Colors.BOLD}🎯 다음 단계:{Colors.END}")
    
    if test_results['server_running']:
        print("1. 대시보드 접속: http://localhost:8002/dashboard")
        print("2. API 문서 확인: http://localhost:8002/docs")
        if data_file:
            print(f"3. 생성된 테스트 데이터로 분석 테스트: {data_file}")
    else:
        print("1. 서버 시작: AIRISS_OneClick.bat 실행")
        print("2. 또는: python -m uvicorn app.main:app --port 8002 --reload")
    
    print("\n💡 도움말:")
    print("- 로그 파일 확인: airiss_v4_test.log")
    print("- 진단 보고서 확인: " + report_filename if 'report_filename' in locals() else "diagnosis_report_*.json")
    print("- 문제 발생 시 GitHub Issues에 보고서를 첨부해주세요")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    # Windows 환경에서 색상 코드 활성화
    if sys.platform == "win32":
        os.system("color")
    
    # 비동기 함수 실행
    asyncio.run(main())
