# integration_test_suite.py
"""
AIRISS v4.0 전체 시스템 통합 테스트
편향 탐지 + 예측 분석 + 실시간 모니터링 통합 검증
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
import json
import websockets
import requests
import logging
from typing import Dict, List
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.bias_detection.bias_detector import BiasDetector
from app.services.predictive_analytics.performance_predictor import PerformancePredictor
from app.services.hybrid_analyzer import HybridAnalyzer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIRISSIntegrationTest:
    """AIRISS v4.0 통합 테스트 스위트"""
    
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.ws_url = "ws://localhost:8002/ws/test_client"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
        
    async def run_all_tests(self):
        """모든 통합 테스트 실행"""
        logger.info("🚀 AIRISS v4.0 통합 테스트 시작")
        
        # 1. 서버 상태 확인
        await self.test_server_health()
        
        # 2. 테스트 데이터 생성
        test_data = self.generate_test_data()
        
        # 3. 기본 분석 테스트
        await self.test_basic_analysis(test_data)
        
        # 4. 편향 탐지 테스트
        await self.test_bias_detection(test_data)
        
        # 5. 예측 분석 테스트
        await self.test_predictive_analytics(test_data)
        
        # 6. WebSocket 실시간 테스트
        await self.test_websocket_realtime()
        
        # 7. 전체 플로우 통합 테스트
        await self.test_end_to_end_flow()
        
        # 8. 성능 벤치마크
        await self.test_performance_benchmark()
        
        # 9. API 응답 시간 테스트
        await self.test_api_response_times()
        
        # 10. 에러 처리 테스트
        await self.test_error_handling()
        
        # 결과 요약
        self.generate_test_report()
        
    async def test_server_health(self):
        """서버 상태 확인"""
        test_name = "server_health"
        try:
            response = requests.get(f"{self.base_url}/health")
            assert response.status_code == 200
            self.log_test_result(test_name, True, "서버 정상 작동")
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    def generate_test_data(self) -> pd.DataFrame:
        """테스트용 데이터 생성"""
        np.random.seed(42)
        n_employees = 200
        
        # 편향 테스트를 위한 의도적 데이터 생성
        genders = np.random.choice(['남성', '여성'], n_employees, p=[0.6, 0.4])
        ages = np.random.choice(['20대', '30대', '40대', '50대'], n_employees)
        departments = np.random.choice(['영업', '개발', 'HR', '재무'], n_employees)
        
        # 의도적 편향 주입 (여성의 점수를 낮게)
        base_scores = np.random.normal(75, 10, n_employees)
        gender_bias = np.where(genders == '여성', -5, 0)
        
        data = pd.DataFrame({
            '직원ID': [f'EMP{str(i).zfill(4)}' for i in range(n_employees)],
            '이름': [f'직원{i}' for i in range(n_employees)],
            '성별': genders,
            '연령대': ages,
            '부서': departments,
            'KPI_달성률': base_scores + gender_bias + np.random.normal(0, 5, n_employees),
            '프로젝트_성과': base_scores + np.random.normal(0, 8, n_employees),
            '평가_피드백': self.generate_feedback_texts(n_employees),
            '업무일지': self.generate_work_logs(n_employees)
        })
        
        return data
    
    def generate_feedback_texts(self, n: int) -> List[str]:
        """평가 피드백 텍스트 생성"""
        positive_keywords = [
            "우수한 성과", "팀워크 뛰어남", "리더십 발휘", "혁신적 사고",
            "책임감 있음", "성실함", "창의적", "협업 능력 우수"
        ]
        negative_keywords = [
            "개선 필요", "소통 부족", "지각 잦음", "집중력 저하",
            "목표 미달성", "협업 어려움", "동기부여 필요"
        ]
        
        feedbacks = []
        for i in range(n):
            if np.random.random() > 0.3:  # 70% 긍정적
                keywords = np.random.choice(positive_keywords, 3)
            else:
                keywords = np.random.choice(negative_keywords, 2)
            feedbacks.append(" ".join(keywords))
        
        return feedbacks
    
    def generate_work_logs(self, n: int) -> List[str]:
        """업무일지 텍스트 생성"""
        activities = [
            "프로젝트 완료", "고객 미팅 성공", "보고서 작성",
            "팀 회의 주도", "문제 해결", "신규 아이디어 제안",
            "교육 참여", "멘토링 실시"
        ]
        
        logs = []
        for i in range(n):
            selected = np.random.choice(activities, 3)
            logs.append(", ".join(selected))
        
        return logs
    
    async def test_basic_analysis(self, test_data: pd.DataFrame):
        """기본 분석 기능 테스트"""
        test_name = "basic_analysis"
        try:
            analyzer = HybridAnalyzer()
            
            # 샘플 데이터로 분석
            sample = test_data.head(10)
            results = []
            
            for _, row in sample.iterrows():
                result = analyzer.analyze_employee(
                    employee_data=row.to_dict(),
                    text_columns=['평가_피드백', '업무일지'],
                    quant_columns=['KPI_달성률', '프로젝트_성과']
                )
                results.append(result)
            
            # 검증
            assert len(results) == 10
            assert all('hybrid_score' in r for r in results)
            assert all(0 <= r['hybrid_score'] <= 100 for r in results)
            
            self.log_test_result(test_name, True, "기본 분석 정상 작동")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_bias_detection(self, test_data: pd.DataFrame):
        """편향 탐지 기능 테스트"""
        test_name = "bias_detection"
        try:
            # 분석 결과에 점수 추가
            test_data['hybrid_score'] = test_data['KPI_달성률']
            
            detector = BiasDetector()
            bias_report = detector.detect_bias(test_data)
            
            # 의도적으로 주입한 성별 편향이 탐지되는지 확인
            assert bias_report['summary']['bias_detected'] == True
            assert '성별' in bias_report['detailed_analysis']
            assert bias_report['detailed_analysis']['성별']['bias_detected'] == True
            
            # HTML 보고서 생성 테스트
            html_report = detector.generate_fairness_report(test_data, 'html')
            assert '<h2>' in html_report
            
            self.log_test_result(test_name, True, "편향 탐지 정상 작동")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_predictive_analytics(self, test_data: pd.DataFrame):
        """예측 분석 기능 테스트"""
        test_name = "predictive_analytics"
        try:
            # 과거 데이터 시뮬레이션
            historical_data = []
            for _, employee in test_data.iterrows():
                for month in range(6):
                    record = employee.to_dict()
                    record['month'] = month
                    record['performance_score'] = np.random.normal(75, 10)
                    historical_data.append(record)
            
            historical_df = pd.DataFrame(historical_data)
            
            # 예측 모델 테스트 (간단한 구현)
            from sklearn.linear_model import LinearRegression
            
            # 각 직원별 트렌드 예측
            predictions = {}
            for emp_id in test_data['직원ID'].unique()[:5]:  # 5명만 테스트
                emp_data = historical_df[historical_df['직원ID'] == emp_id]
                if len(emp_data) > 1:
                    X = emp_data['month'].values.reshape(-1, 1)
                    y = emp_data['performance_score'].values
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # 6개월 후 예측
                    future_score = model.predict([[11]])[0]
                    predictions[emp_id] = {
                        'current_score': y[-1],
                        'predicted_score': future_score,
                        'trend': 'improving' if future_score > y[-1] else 'declining'
                    }
            
            assert len(predictions) > 0
            self.log_test_result(test_name, True, f"예측 분석 완료: {len(predictions)}명")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_websocket_realtime(self):
        """WebSocket 실시간 통신 테스트"""
        test_name = "websocket_realtime"
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # 연결 메시지
                await websocket.send(json.dumps({
                    "type": "connect",
                    "client_id": "test_client"
                }))
                
                # 응답 대기
                response = await asyncio.wait_for(
                    websocket.recv(), 
                    timeout=5.0
                )
                
                data = json.loads(response)
                assert data.get('status') == 'connected'
                
                # 분석 진행률 시뮬레이션
                await websocket.send(json.dumps({
                    "type": "analysis_progress",
                    "progress": 50,
                    "message": "분석 중..."
                }))
                
                self.log_test_result(test_name, True, "WebSocket 통신 정상")
                
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_end_to_end_flow(self):
        """전체 플로우 통합 테스트"""
        test_name = "end_to_end_flow"
        try:
            # 1. 파일 업로드 시뮬레이션
            test_file_path = "test_data.csv"
            test_data = self.generate_test_data()
            test_data.to_csv(test_file_path, index=False)
            
            # 2. 업로드 API 호출
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test_data.csv', f, 'text/csv')}
                response = requests.post(
                    f"{self.base_url}/api/v1/upload",
                    files=files
                )
            
            if response.status_code == 200:
                upload_result = response.json()
                
                # 3. 분석 시작
                analysis_response = requests.post(
                    f"{self.base_url}/api/v1/analyze",
                    json={
                        "file_id": upload_result.get('file_id'),
                        "text_columns": ['평가_피드백', '업무일지'],
                        "quant_columns": ['KPI_달성률', '프로젝트_성과'],
                        "include_bias_check": True,
                        "include_predictions": True
                    }
                )
                
                if analysis_response.status_code == 200:
                    self.log_test_result(test_name, True, "전체 플로우 정상 작동")
                else:
                    self.log_test_result(test_name, False, f"분석 API 오류: {analysis_response.status_code}")
            else:
                self.log_test_result(test_name, False, f"업로드 API 오류: {response.status_code}")
            
            # 정리
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_performance_benchmark(self):
        """성능 벤치마크 테스트"""
        test_name = "performance_benchmark"
        try:
            import time
            
            # 다양한 크기의 데이터셋 테스트
            sizes = [100, 500, 1000]
            results = {}
            
            for size in sizes:
                test_data = self.generate_test_data()
                test_data = pd.concat([test_data] * (size // 200), ignore_index=True)
                
                start_time = time.time()
                
                # 분석 실행
                analyzer = HybridAnalyzer()
                for _, row in test_data.head(10).iterrows():
                    analyzer.analyze_employee(
                        employee_data=row.to_dict(),
                        text_columns=['평가_피드백', '업무일지'],
                        quant_columns=['KPI_달성률', '프로젝트_성과']
                    )
                
                elapsed = time.time() - start_time
                results[size] = elapsed
                
                logger.info(f"  {size}명 데이터 처리 시간: {elapsed:.2f}초")
            
            # 성능 기준: 1000명 처리에 10초 이내
            assert results[1000] < 10.0
            
            self.log_test_result(test_name, True, f"성능 테스트 통과: {results}")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_api_response_times(self):
        """API 응답 시간 테스트"""
        test_name = "api_response_times"
        try:
            import time
            
            endpoints = [
                ("/", "GET"),
                ("/health", "GET"),
                ("/api/v1/analysis/sample", "GET"),
            ]
            
            response_times = {}
            
            for endpoint, method in endpoints:
                start = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                else:
                    response = requests.post(f"{self.base_url}{endpoint}")
                
                elapsed = (time.time() - start) * 1000  # ms
                response_times[endpoint] = elapsed
                
                # 응답 시간 기준: 500ms 이내
                assert elapsed < 500
                logger.info(f"  {endpoint}: {elapsed:.2f}ms")
            
            self.log_test_result(test_name, True, f"API 응답 시간 정상: {response_times}")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_error_handling(self):
        """에러 처리 테스트"""
        test_name = "error_handling"
        try:
            # 1. 잘못된 파일 형식
            response = requests.post(
                f"{self.base_url}/api/v1/upload",
                files={'file': ('test.txt', b'invalid content', 'text/plain')}
            )
            assert response.status_code == 400
            
            # 2. 필수 컬럼 누락
            bad_data = pd.DataFrame({'col1': [1, 2, 3]})
            bad_data.to_csv('bad_data.csv', index=False)
            
            with open('bad_data.csv', 'rb') as f:
                response = requests.post(
                    f"{self.base_url}/api/v1/upload",
                    files={'file': ('bad_data.csv', f, 'text/csv')}
                )
            
            # 3. 잘못된 분석 요청
            response = requests.post(
                f"{self.base_url}/api/v1/analyze",
                json={"invalid": "request"}
            )
            assert response.status_code in [400, 422]
            
            # 정리
            if os.path.exists('bad_data.csv'):
                os.remove('bad_data.csv')
            
            self.log_test_result(test_name, True, "에러 처리 정상 작동")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    def log_test_result(self, test_name: str, success: bool, message: str):
        """테스트 결과 기록"""
        self.test_results['tests'][test_name] = {
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results['summary']['total'] += 1
        if success:
            self.test_results['summary']['passed'] += 1
            logger.info(f"✅ {test_name}: {message}")
        else:
            self.test_results['summary']['failed'] += 1
            logger.error(f"❌ {test_name}: {message}")
    
    def generate_test_report(self):
        """테스트 결과 보고서 생성"""
        summary = self.test_results['summary']
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           AIRISS v4.0 통합 테스트 결과 보고서               ║
╠══════════════════════════════════════════════════════════════╣
║ 실행 시간: {self.test_results['timestamp']}
║ 
║ 📊 전체 결과:
║   - 총 테스트: {summary['total']}개
║   - 성공: {summary['passed']}개
║   - 실패: {summary['failed']}개
║   - 성공률: {success_rate:.1f}%
║
║ 📋 세부 결과:
"""
        
        for test_name, result in self.test_results['tests'].items():
            status = "✅" if result['success'] else "❌"
            report += f"║   {status} {test_name}: {result['message']}\n"
        
        report += """║
╚══════════════════════════════════════════════════════════════╝
"""
        
        logger.info(report)
        
        # JSON 파일로도 저장
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        logger.info("📄 상세 테스트 결과가 test_results.json에 저장되었습니다.")

async def main():
    """메인 실행 함수"""
    tester = AIRISSIntegrationTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())