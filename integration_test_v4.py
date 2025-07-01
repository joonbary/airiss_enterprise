#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 통합 테스트
시스템의 주요 기능이 정상 작동하는지 확인합니다.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# 프로젝트 경로 설정
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class AIRISSIntegrationTest:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        self.test_count = 0
        self.success_count = 0
        
    def print_test_header(self, test_name):
        """테스트 헤더 출력"""
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
        
    def test_import_modules(self):
        """모듈 import 테스트"""
        self.print_test_header("모듈 Import 테스트")
        
        modules_to_test = {
            "text_analyzer": "app.services.text_analyzer",
            "quantitative_analyzer": "app.services.quantitative_analyzer",
            "hybrid_analyzer": "app.services.hybrid_analyzer",
            "websocket_manager": "app.core.websocket_manager",
            "sqlite_service": "app.db.sqlite_service"
        }
        
        for name, module_path in modules_to_test.items():
            try:
                module = __import__(module_path, fromlist=[''])
                self.results["tests"][f"import_{name}"] = "PASS"
                self.success_count += 1
                print(f"✅ {name}: 성공")
            except Exception as e:
                self.results["tests"][f"import_{name}"] = f"FAIL: {str(e)}"
                print(f"❌ {name}: 실패 - {str(e)}")
            self.test_count += 1
            
    def test_text_analyzer(self):
        """텍스트 분석기 테스트"""
        self.print_test_header("텍스트 분석기 테스트")
        
        try:
            from app.services.text_analyzer import AIRISSTextAnalyzer
            
            # 분석기 생성
            analyzer = AIRISSTextAnalyzer()
            print("✅ 텍스트 분석기 생성 성공")
            
            # 테스트 케이스
            test_cases = [
                ("업무에서 탁월한 성과를 보였고 목표를 초과 달성했습니다.", "업무성과"),
                ("팀원들과 적극적으로 협력하며 리더십을 발휘했습니다.", "리더십협업"),
                ("새로운 아이디어를 제시하고 혁신적인 해결책을 찾았습니다.", "혁신창의")
            ]
            
            for text, dimension in test_cases:
                result = analyzer.analyze_text(text, dimension)
                score = result.get('score', 0)
                print(f"  📝 '{text[:30]}...' → {dimension}: {score}점")
                
                if score > 0:
                    self.results["tests"][f"text_analysis_{dimension}"] = f"PASS: {score}"
                    self.success_count += 1
                else:
                    self.results["tests"][f"text_analysis_{dimension}"] = "FAIL: score=0"
                self.test_count += 1
                
        except Exception as e:
            self.results["tests"]["text_analyzer"] = f"FAIL: {str(e)}"
            print(f"❌ 텍스트 분석기 테스트 실패: {e}")
            self.test_count += 1
            
    def test_quantitative_analyzer(self):
        """정량 분석기 테스트"""
        self.print_test_header("정량 분석기 테스트")
        
        try:
            from app.services.quantitative_analyzer import QuantitativeAnalyzer
            
            # 분석기 생성
            analyzer = QuantitativeAnalyzer()
            print("✅ 정량 분석기 생성 성공")
            
            # 테스트 데이터
            test_data = pd.Series({
                'uid': 'TEST001',
                '업무성과': 85,
                'KPI달성률': 92,
                '프로젝트참여': 5,
                '교육이수시간': 40
            })
            
            # 정량 데이터 추출
            quant_data = analyzer.extract_quantitative_data(test_data)
            print(f"  📊 추출된 정량 데이터: {len(quant_data)}개 항목")
            
            # 점수 계산
            result = analyzer.calculate_quantitative_score(quant_data)
            score = result.get('quantitative_score', 0)
            print(f"  📊 정량 분석 점수: {score}점")
            
            if score > 0:
                self.results["tests"]["quantitative_analysis"] = f"PASS: {score}"
                self.success_count += 1
            else:
                self.results["tests"]["quantitative_analysis"] = "FAIL: score=0"
            self.test_count += 1
            
        except Exception as e:
            self.results["tests"]["quantitative_analyzer"] = f"FAIL: {str(e)}"
            print(f"❌ 정량 분석기 테스트 실패: {e}")
            self.test_count += 1
            
    def test_hybrid_analyzer(self):
        """하이브리드 분석기 테스트"""
        self.print_test_header("하이브리드 분석기 테스트")
        
        try:
            from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
            
            # 분석기 생성
            analyzer = AIRISSHybridAnalyzer()
            print("✅ 하이브리드 분석기 생성 성공")
            
            # 테스트 데이터
            test_uid = "TEST001"
            test_opinion = """
            이번 분기에 맡은 프로젝트를 성공적으로 완수했습니다.
            팀원들과의 협력을 통해 어려운 문제를 해결했고,
            새로운 프로세스를 도입하여 효율성을 20% 향상시켰습니다.
            고객 만족도도 크게 개선되었습니다.
            """
            
            test_row = pd.Series({
                'uid': test_uid,
                '업무성과': 88,
                'KPI달성률': 95,
                '리더십협업': 85,
                '커뮤니케이션': 82,
                '프로젝트참여': 6,
                '교육이수시간': 45,
                '성별': '남성',
                '연령대': '30대',
                '부서': '개발팀',
                '직급': '대리'
            })
            
            # 종합 분석 실행
            result = analyzer.comprehensive_analysis(test_uid, test_opinion, test_row)
            
            # 결과 확인
            hybrid_score = result['hybrid_analysis']['overall_score']
            grade = result['hybrid_analysis']['grade']
            
            print(f"\n  📋 분석 결과:")
            print(f"     - 텍스트 점수: {result['text_analysis']['overall_score']}점")
            print(f"     - 정량 점수: {result['quantitative_analysis']['quantitative_score']}점")
            print(f"     - 하이브리드 점수: {hybrid_score}점")
            print(f"     - 등급: {grade}")
            
            if hybrid_score > 0:
                self.results["tests"]["hybrid_analysis"] = f"PASS: {hybrid_score}"
                self.success_count += 1
            else:
                self.results["tests"]["hybrid_analysis"] = "FAIL: score=0"
            self.test_count += 1
            
            # 공정성 메트릭 테스트
            fairness_metrics = analyzer.get_fairness_metrics()
            print(f"\n  📊 공정성 메트릭: {fairness_metrics.get('total_analyzed', 0)}개 분석 완료")
            
        except Exception as e:
            self.results["tests"]["hybrid_analyzer"] = f"FAIL: {str(e)}"
            print(f"❌ 하이브리드 분석기 테스트 실패: {e}")
            self.test_count += 1
            
    def test_database_connection(self):
        """데이터베이스 연결 테스트"""
        self.print_test_header("데이터베이스 연결 테스트")
        
        try:
            import aiosqlite
            import asyncio
            
            async def test_db():
                db_path = project_root / "airiss.db"
                
                if not db_path.exists():
                    print(f"⚠️  데이터베이스 파일이 없습니다: {db_path}")
                    return False
                    
                try:
                    async with aiosqlite.connect(str(db_path)) as db:
                        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = await cursor.fetchall()
                        print(f"✅ 데이터베이스 연결 성공")
                        print(f"  📋 테이블 수: {len(tables)}")
                        for table in tables:
                            print(f"     - {table[0]}")
                        return True
                except Exception as e:
                    print(f"❌ 데이터베이스 연결 실패: {e}")
                    return False
            
            # 비동기 테스트 실행
            success = asyncio.run(test_db())
            
            if success:
                self.results["tests"]["database_connection"] = "PASS"
                self.success_count += 1
            else:
                self.results["tests"]["database_connection"] = "FAIL"
            self.test_count += 1
            
        except Exception as e:
            self.results["tests"]["database_connection"] = f"FAIL: {str(e)}"
            print(f"❌ 데이터베이스 테스트 실패: {e}")
            self.test_count += 1
            
    def test_api_endpoints(self):
        """API 엔드포인트 테스트 (서버가 실행 중인 경우)"""
        self.print_test_header("API 엔드포인트 테스트")
        
        try:
            import httpx
            import asyncio
            
            async def test_endpoints():
                base_url = "http://localhost:8002"
                endpoints = [
                    ("/api", "API 정보"),
                    ("/health", "헬스체크"),
                    ("/health/db", "DB 헬스체크"),
                    ("/health/analysis", "분석 엔진 헬스체크")
                ]
                
                async with httpx.AsyncClient() as client:
                    for endpoint, description in endpoints:
                        try:
                            response = await client.get(f"{base_url}{endpoint}", timeout=5.0)
                            if response.status_code == 200:
                                print(f"✅ {endpoint} ({description}): OK")
                                self.results["tests"][f"api_{endpoint}"] = "PASS"
                                self.success_count += 1
                            else:
                                print(f"⚠️  {endpoint}: 상태 코드 {response.status_code}")
                                self.results["tests"][f"api_{endpoint}"] = f"FAIL: {response.status_code}"
                        except Exception as e:
                            print(f"❌ {endpoint}: 연결 실패")
                            self.results["tests"][f"api_{endpoint}"] = "FAIL: connection error"
                        self.test_count += 1
            
            # 서버 연결 시도
            print("🔍 로컬 서버 (http://localhost:8002) 연결 시도...")
            asyncio.run(test_endpoints())
            
        except Exception as e:
            print(f"⚠️  API 테스트 스킵: 서버가 실행 중이 아닙니다")
            self.results["tests"]["api_endpoints"] = "SKIPPED: server not running"
            
    def generate_summary(self):
        """테스트 요약 생성"""
        self.print_test_header("테스트 결과 요약")
        
        # 성공률 계산
        success_rate = (self.success_count / self.test_count * 100) if self.test_count > 0 else 0
        
        self.results["summary"] = {
            "total_tests": self.test_count,
            "passed": self.success_count,
            "failed": self.test_count - self.success_count,
            "success_rate": round(success_rate, 1)
        }
        
        print(f"\n📊 전체 테스트: {self.test_count}개")
        print(f"✅ 성공: {self.success_count}개")
        print(f"❌ 실패: {self.test_count - self.success_count}개")
        print(f"📈 성공률: {success_rate:.1f}%")
        
        # 시스템 상태 판단
        if success_rate >= 90:
            print("\n✅ 시스템 상태: 우수")
            print("   AIRISS v4.0이 정상적으로 작동하고 있습니다!")
        elif success_rate >= 70:
            print("\n⚠️  시스템 상태: 양호")
            print("   일부 기능에 문제가 있지만 기본 기능은 작동합니다.")
        else:
            print("\n❌ 시스템 상태: 문제 발생")
            print("   시스템에 심각한 문제가 있습니다. 점검이 필요합니다.")
            
        # 보고서 저장
        report_path = project_root / "integration_test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 상세 보고서 저장: {report_path}")
        
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 AIRISS v4.0 통합 테스트 시작")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_import_modules()
        self.test_text_analyzer()
        self.test_quantitative_analyzer()
        self.test_hybrid_analyzer()
        self.test_database_connection()
        self.test_api_endpoints()
        self.generate_summary()
        
        print("\n✅ 통합 테스트 완료!")

if __name__ == "__main__":
    tester = AIRISSIntegrationTest()
    tester.run_all_tests()
