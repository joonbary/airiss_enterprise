# app/core/file_processor.py
"""
AIRISS v4.0 파일 처리 모듈
- Excel/CSV 파일 파싱
- 데이터 검증 및 정리
- 컬럼 자동 감지
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileProcessor:
    """파일 처리 및 데이터 추출 클래스"""
    
    def __init__(self):
        self.supported_extensions = ['.xlsx', '.xls', '.csv']
        self.encoding_list = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']
        
        # 컬럼 감지 키워드
        self.column_patterns = {
            'uid': ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp', '사원번호', '직원번호'],
            'opinion': ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', '피드백', 
                       'comment', 'review', '평가의견', '종합의견', '상사의견'],
            'quantitative': {
                'score': ['점수', 'score', '평점', 'rating', '점'],
                'grade': ['등급', 'grade', '평가', 'level', '평가등급'],
                'rate': ['달성률', '비율', 'rate', '%', 'percent', '퍼센트'],
                'count': ['횟수', '건수', 'count', '회', '번']
            }
        }
        
        # 기본 컬럼명 매핑
        self.column_mapping = {}
        
    async def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """파일 처리 메인 함수"""
        try:
            # 파일 확장자 확인
            file_ext = self._get_file_extension(filename)
            if file_ext not in self.supported_extensions:
                raise ValueError(f"지원하지 않는 파일 형식입니다: {file_ext}")
            
            # 파일 읽기
            if file_ext in ['.xlsx', '.xls']:
                df = await self._read_excel(file_content)
            else:  # CSV
                df = await self._read_csv(file_content)
            
            # 데이터 검증
            validation_result = self._validate_dataframe(df)
            if not validation_result['is_valid']:
                raise ValueError(validation_result['message'])
            
            # 컬럼 분석
            column_analysis = self._analyze_columns(df)
            
            # 데이터 정리
            cleaned_df = self._clean_data(df, column_analysis)
            
            # 데이터 품질 평가
            data_quality = self._assess_data_quality(cleaned_df, column_analysis)
            
            return {
                'success': True,
                'dataframe': cleaned_df,
                'total_records': len(cleaned_df),
                'column_analysis': column_analysis,
                'data_quality': data_quality,
                'processing_info': {
                    'filename': filename,
                    'file_size': len(file_content),
                    'processed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"파일 처리 오류: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        return '.' + filename.split('.')[-1].lower()
    
    async def _read_excel(self, content: bytes) -> pd.DataFrame:
        """Excel 파일 읽기"""
        try:
            # 여러 시트가 있는 경우 첫 번째 시트 사용
            excel_file = pd.ExcelFile(io.BytesIO(content))
            sheet_names = excel_file.sheet_names
            
            if len(sheet_names) > 1:
                logger.info(f"여러 시트 발견: {sheet_names}. 첫 번째 시트 사용")
            
            df = pd.read_excel(io.BytesIO(content), sheet_name=0)
            logger.info(f"Excel 파일 읽기 완료: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Excel 읽기 오류: {str(e)}")
            raise ValueError(f"Excel 파일을 읽을 수 없습니다: {str(e)}")
    
    async def _read_csv(self, content: bytes) -> pd.DataFrame:
        """CSV 파일 읽기 (여러 인코딩 시도)"""
        last_error = None
        
        for encoding in self.encoding_list:
            try:
                df = pd.read_csv(io.StringIO(content.decode(encoding)))
                logger.info(f"CSV 파일 읽기 성공 (인코딩: {encoding}): {len(df)} rows")
                return df
            except Exception as e:
                last_error = e
                continue
        
        raise ValueError(f"CSV 파일 인코딩을 인식할 수 없습니다. 마지막 오류: {str(last_error)}")
    
    def _validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터프레임 검증"""
        # 빈 데이터프레임 체크
        if df.empty:
            return {'is_valid': False, 'message': '데이터가 없습니다'}
        
        # 최소 행 수 체크
        if len(df) < 1:
            return {'is_valid': False, 'message': '최소 1개 이상의 데이터가 필요합니다'}
        
        # 최소 컬럼 수 체크
        if len(df.columns) < 2:
            return {'is_valid': False, 'message': '최소 2개 이상의 컬럼이 필요합니다'}
        
        # 모든 값이 null인 행 제거
        df_cleaned = df.dropna(how='all')
        if len(df_cleaned) == 0:
            return {'is_valid': False, 'message': '유효한 데이터가 없습니다'}
        
        return {'is_valid': True, 'message': 'OK'}
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """컬럼 분석 및 자동 감지"""
        columns = list(df.columns)
        analysis = {
            'total_columns': len(columns),
            'uid_columns': [],
            'opinion_columns': [],
            'quantitative_columns': {},
            'other_columns': [],
            'column_types': {}
        }
        
        # UID 컬럼 찾기
        for col in columns:
            col_lower = str(col).lower()
            for pattern in self.column_patterns['uid']:
                if pattern in col_lower:
                    analysis['uid_columns'].append(col)
                    analysis['column_types'][col] = 'uid'
                    break
        
        # 의견 컬럼 찾기
        for col in columns:
            if col in analysis['uid_columns']:
                continue
            col_lower = str(col).lower()
            for pattern in self.column_patterns['opinion']:
                if pattern in col_lower:
                    analysis['opinion_columns'].append(col)
                    analysis['column_types'][col] = 'opinion'
                    break
        
        # 정량 데이터 컬럼 찾기
        for category, patterns in self.column_patterns['quantitative'].items():
            analysis['quantitative_columns'][category] = []
            for col in columns:
                if col in analysis['uid_columns'] or col in analysis['opinion_columns']:
                    continue
                col_lower = str(col).lower()
                for pattern in patterns:
                    if pattern in col_lower:
                        # 실제 데이터 확인
                        if self._is_quantitative_column(df[col]):
                            analysis['quantitative_columns'][category].append(col)
                            analysis['column_types'][col] = f'quantitative_{category}'
                            break
        
        # 기타 컬럼
        identified_columns = (
            analysis['uid_columns'] + 
            analysis['opinion_columns'] + 
            sum(analysis['quantitative_columns'].values(), [])
        )
        analysis['other_columns'] = [col for col in columns if col not in identified_columns]
        
        # 자동 감지 실패 시 기본값 설정
        if not analysis['uid_columns'] and columns:
            # 첫 번째 컬럼을 UID로 가정
            analysis['uid_columns'] = [columns[0]]
            analysis['column_types'][columns[0]] = 'uid'
            logger.warning(f"UID 컬럼 자동 감지 실패. '{columns[0]}'을 UID로 사용")
        
        if not analysis['opinion_columns'] and len(columns) > 1:
            # 텍스트가 가장 많은 컬럼을 의견으로 가정
            text_col = self._find_text_column(df)
            if text_col:
                analysis['opinion_columns'] = [text_col]
                analysis['column_types'][text_col] = 'opinion'
                logger.warning(f"의견 컬럼 자동 감지 실패. '{text_col}'을 의견으로 사용")
        
        return analysis
    
    def _is_quantitative_column(self, series: pd.Series, sample_size: int = 10) -> bool:
        """컬럼이 정량 데이터인지 확인"""
        sample = series.dropna().head(sample_size)
        if len(sample) == 0:
            return False
        
        quantitative_count = 0
        for value in sample:
            str_val = str(value).strip()
            # 숫자, 등급, 퍼센트 패턴 확인
            if (str_val.replace('.', '').replace('%', '').replace('점', '').isdigit() or
                any(grade in str_val.upper() for grade in ['A', 'B', 'C', 'D', 'S', '우수', '양호', '보통']) or
                any(str_val.startswith(str(i)) for i in range(1, 6))):
                quantitative_count += 1
        
        # 70% 이상이 정량적이면 정량 컬럼으로 판단
        return (quantitative_count / len(sample)) >= 0.7
    
    def _find_text_column(self, df: pd.DataFrame) -> Optional[str]:
        """텍스트가 가장 많은 컬럼 찾기"""
        text_scores = {}
        
        for col in df.columns:
            # 평균 텍스트 길이 계산
            try:
                avg_length = df[col].dropna().astype(str).str.len().mean()
                text_scores[col] = avg_length
            except:
                text_scores[col] = 0
        
        if text_scores:
            return max(text_scores, key=text_scores.get)
        return None
    
    def _clean_data(self, df: pd.DataFrame, column_analysis: Dict[str, Any]) -> pd.DataFrame:
        """데이터 정리 및 전처리"""
        cleaned_df = df.copy()
        
        # 빈 행 제거
        cleaned_df = cleaned_df.dropna(how='all')
        
        # UID 컬럼 정리
        if column_analysis['uid_columns']:
            uid_col = column_analysis['uid_columns'][0]
            # UID를 문자열로 변환하고 공백 제거
            cleaned_df[uid_col] = cleaned_df[uid_col].astype(str).str.strip()
            # 빈 UID는 자동 생성
            empty_mask = cleaned_df[uid_col].isin(['', 'nan', 'None'])
            cleaned_df.loc[empty_mask, uid_col] = [f"EMP_{i:04d}" for i in range(sum(empty_mask))]
        
        # 의견 컬럼 정리
        for col in column_analysis['opinion_columns']:
            # NaN을 빈 문자열로 변환
            cleaned_df[col] = cleaned_df[col].fillna('')
            # 문자열 변환 및 공백 정리
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        
        # 정량 데이터 정리
        for category, columns in column_analysis['quantitative_columns'].items():
            for col in columns:
                # 숫자가 아닌 값 처리
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        # 중복 제거 (UID 기준)
        if column_analysis['uid_columns']:
            uid_col = column_analysis['uid_columns'][0]
            cleaned_df = cleaned_df.drop_duplicates(subset=[uid_col], keep='first')
        
        logger.info(f"데이터 정리 완료: {len(df)} → {len(cleaned_df)} rows")
        
        return cleaned_df.reset_index(drop=True)
    
    def _assess_data_quality(self, df: pd.DataFrame, column_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 품질 평가"""
        quality = {
            'overall_score': 0,
            'completeness': {},
            'issues': [],
            'recommendations': []
        }
        
        # 전체 완전성
        total_cells = df.size
        non_empty_cells = df.notna().sum().sum()
        completeness_rate = (non_empty_cells / total_cells) * 100 if total_cells > 0 else 0
        quality['completeness']['overall'] = round(completeness_rate, 1)
        
        # UID 완전성
        if column_analysis['uid_columns']:
            uid_col = column_analysis['uid_columns'][0]
            uid_completeness = (df[uid_col].notna().sum() / len(df)) * 100
            quality['completeness']['uid'] = round(uid_completeness, 1)
            
            if uid_completeness < 100:
                quality['issues'].append("일부 직원 ID가 누락되어 있습니다")
                quality['recommendations'].append("모든 직원에게 고유 ID를 부여하세요")
        
        # 의견 완전성
        if column_analysis['opinion_columns']:
            opinion_col = column_analysis['opinion_columns'][0]
            non_empty_opinions = df[opinion_col].str.len() > 10  # 최소 10자 이상
            opinion_completeness = (non_empty_opinions.sum() / len(df)) * 100
            quality['completeness']['opinion'] = round(opinion_completeness, 1)
            
            if opinion_completeness < 80:
                quality['issues'].append("평가 의견이 부실한 데이터가 많습니다")
                quality['recommendations'].append("구체적이고 상세한 평가 의견 작성을 권장합니다")
        
        # 정량 데이터 완전성
        quant_columns = sum(column_analysis['quantitative_columns'].values(), [])
        if quant_columns:
            quant_completeness = (df[quant_columns].notna().sum().sum() / 
                                (len(df) * len(quant_columns))) * 100
            quality['completeness']['quantitative'] = round(quant_completeness, 1)
            
            if quant_completeness < 60:
                quality['issues'].append("정량 평가 데이터가 부족합니다")
                quality['recommendations'].append("객관적인 평가 지표를 추가로 수집하세요")
        
        # 전체 품질 점수 계산
        scores = list(quality['completeness'].values())
        quality['overall_score'] = round(sum(scores) / len(scores), 1) if scores else 0
        
        # 품질 등급
        if quality['overall_score'] >= 90:
            quality['grade'] = '매우 좋음'
        elif quality['overall_score'] >= 75:
            quality['grade'] = '좋음'
        elif quality['overall_score'] >= 60:
            quality['grade'] = '보통'
        else:
            quality['grade'] = '개선 필요'
        
        return quality
    
    def get_sample_data(self, df: pd.DataFrame, column_analysis: Dict[str, Any], 
                       sample_size: int = 5) -> List[Dict[str, Any]]:
        """분석용 샘플 데이터 추출"""
        samples = []
        
        # 샘플 크기 조정
        actual_sample_size = min(sample_size, len(df))
        
        # 랜덤 샘플링
        sample_df = df.sample(n=actual_sample_size, random_state=42)
        
        for _, row in sample_df.iterrows():
            sample = {}
            
            # UID 추출
            if column_analysis['uid_columns']:
                sample['uid'] = row[column_analysis['uid_columns'][0]]
            else:
                sample['uid'] = f"UNKNOWN_{_}"
            
            # 의견 추출
            if column_analysis['opinion_columns']:
                sample['opinion'] = row[column_analysis['opinion_columns'][0]]
            else:
                sample['opinion'] = ""
            
            # 정량 데이터 추출
            for category, columns in column_analysis['quantitative_columns'].items():
                for col in columns:
                    sample[col] = row[col]
            
            # 기타 컬럼도 포함
            for col in column_analysis['other_columns']:
                sample[col] = row[col]
            
            samples.append(sample)
        
        return samples