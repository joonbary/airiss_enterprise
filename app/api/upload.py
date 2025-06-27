# app/api/upload.py
# AIRISS v4.0 파일 업로드 API - SQLiteService 메서드 호출 오류 완전 해결 버전
# async/await 처리 + 올바른 인자 전달

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import io
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import traceback

# 프로젝트 내 모듈 import
from app.db.sqlite_service import SQLiteService
from app.schemas.schemas import FileUploadResponse, FileInfoResponse

# 로깅 설정
logger = logging.getLogger(__name__)

# 업로드 라우터 생성
router = APIRouter(prefix="/upload", tags=["upload"])

# SQLiteService 의존성 주입
def get_sqlite_service() -> SQLiteService:
    service = SQLiteService()
    # 데이터베이스 초기화를 동기적으로 실행하는 것은 문제가 될 수 있으므로
    # 실제 사용 시점에서 초기화하도록 변경
    return service

@router.post("/upload/", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db_service: SQLiteService = Depends(get_sqlite_service)
):
    """
    파일 업로드 및 AIRISS v4.0 하이브리드 분석을 위한 데이터 전처리
    - Excel (.xlsx, .xls) 및 CSV 파일 지원
    - 텍스트 + 정량데이터 자동 감지
    - SQLiteService DB 통합 저장
    """
    
    file_id = None
    try:
        # 🔥 데이터베이스 초기화 (한 번만 실행)
        try:
            await db_service.init_database()
        except Exception as e:
            logger.warning(f"데이터베이스 초기화 건너뜀 (이미 초기화됨): {e}")
        
        # 파일 유효성 검사
        if not file.filename:
            raise HTTPException(status_code=400, detail="파일명이 없습니다")
        
        # 지원되는 파일 형식 확인
        supported_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = None
        for ext in supported_extensions:
            if file.filename.lower().endswith(ext):
                file_extension = ext
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=400, 
                detail=f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(supported_extensions)}"
            )
        
        logger.info(f"📁 파일 업로드 시작: {file.filename} ({file_extension})")
        
        # 파일 내용 읽기
        try:
            file_contents = await file.read()
            if len(file_contents) == 0:
                raise HTTPException(status_code=400, detail="빈 파일입니다")
            
            logger.info(f"📊 파일 크기: {len(file_contents)} bytes")
            
        except Exception as e:
            logger.error(f"파일 읽기 오류: {str(e)}")
            raise HTTPException(status_code=400, detail=f"파일을 읽을 수 없습니다: {str(e)}")
        
        # DataFrame 생성
        df = None
        try:
            if file_extension in ['.xlsx', '.xls']:
                # Excel 파일 처리
                df = pd.read_excel(io.BytesIO(file_contents))
                logger.info("✅ Excel 파일 파싱 완료")
                
            elif file_extension == '.csv':
                # CSV 파일 처리 (다중 인코딩 시도)
                encodings = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1', 'latin1']
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(io.StringIO(file_contents.decode(encoding)))
                        logger.info(f"✅ CSV 파일 파싱 완료 (인코딩: {encoding})")
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                    except Exception as e:
                        logger.warning(f"CSV 파싱 시도 실패 ({encoding}): {str(e)}")
                        continue
                
                if df is None:
                    raise HTTPException(
                        status_code=400, 
                        detail="CSV 파일 인코딩을 인식할 수 없습니다. UTF-8, CP949, EUC-KR 인코딩을 지원합니다."
                    )
        
        except Exception as e:
            logger.error(f"DataFrame 생성 오류: {str(e)}")
            raise HTTPException(status_code=400, detail=f"파일 형식을 파싱할 수 없습니다: {str(e)}")
        
        # DataFrame 기본 검증
        if df is None:
            raise HTTPException(status_code=400, detail="DataFrame 생성에 실패했습니다")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="파일에 데이터가 없습니다")
        
        if len(df.columns) == 0:
            raise HTTPException(status_code=400, detail="파일에 컬럼이 없습니다")
        
        # 🔥 안전한 컬럼 정보 추출
        try:
            # 컬럼명을 문자열로 변환하여 안전하게 처리
            all_columns = [str(col).strip() for col in df.columns.tolist()]
            
            # 빈 컬럼명 제거
            all_columns = [col for col in all_columns if col and col != 'nan' and col != 'None']
            
            if not all_columns:
                raise HTTPException(status_code=400, detail="유효한 컬럼명이 없습니다")
            
            logger.info(f"📋 추출된 컬럼: {all_columns}")
            
        except Exception as e:
            logger.error(f"컬럼 정보 추출 오류: {str(e)}")
            raise HTTPException(status_code=400, detail=f"컬럼 정보를 추출할 수 없습니다: {str(e)}")
        
        # AIRISS v4.0 컬럼 분류 (기존 로직 유지)
        try:
            # UID 컬럼 찾기
            uid_columns = []
            uid_keywords = ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp', '사용자']
            for col in all_columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in uid_keywords):
                    uid_columns.append(col)
            
            # 의견/텍스트 컬럼 찾기  
            opinion_columns = []
            opinion_keywords = ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', '피드백', 'comment', 'review', '설명']
            for col in all_columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in opinion_keywords):
                    opinion_columns.append(col)
            
            # 🆕 정량데이터 컬럼 찾기 (AIRISS v4.0 하이브리드 분석용)
            quantitative_columns = []
            quant_keywords = ['점수', 'score', '평점', 'rating', '등급', 'grade', 'level', 
                            '달성률', '비율', 'rate', '%', 'percent', '횟수', '건수', 'count']
            
            for col in all_columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in quant_keywords):
                    # 실제 데이터가 정량적인지 샘플 검증
                    try:
                        sample_data = df[col].dropna().head(10)
                        if len(sample_data) > 0:
                            quantitative_score = 0
                            for value in sample_data:
                                str_val = str(value).strip()
                                # 숫자, 등급, 퍼센트 패턴 확인
                                if (str_val.replace('.', '').replace('%', '').replace('점', '').replace('-', '').isdigit() or
                                    any(grade in str_val.upper() for grade in ['A', 'B', 'C', 'D', 'S', 'F']) or
                                    any(grade in str_val for grade in ['우수', '양호', '보통', '미흡', '부족']) or
                                    any(grade in str_val for grade in ['1', '2', '3', '4', '5'])):
                                    quantitative_score += 1
                            
                            # 샘플의 70% 이상이 정량적이면 정량 컬럼으로 분류
                            if len(sample_data) > 0 and (quantitative_score / len(sample_data)) >= 0.7:
                                quantitative_columns.append(col)
                    except Exception as e:
                        logger.warning(f"정량 컬럼 검증 중 오류 ({col}): {str(e)}")
                        continue
            
            logger.info(f"🔍 UID 컬럼: {uid_columns}")
            logger.info(f"💬 의견 컬럼: {opinion_columns}")
            logger.info(f"📊 정량 컬럼: {quantitative_columns}")
            
        except Exception as e:
            logger.error(f"컬럼 분류 오류: {str(e)}")
            raise HTTPException(status_code=400, detail=f"컬럼 분류 중 오류가 발생했습니다: {str(e)}")
        
        # 📊 데이터 품질 분석
        try:
            total_records = len(df)
            
            # 의견 컬럼 기준 비어있지 않은 레코드 수
            text_non_empty = 0
            if opinion_columns:
                text_non_empty = len(df.dropna(subset=opinion_columns))
            
            # 정량 컬럼 기준 비어있지 않은 레코드 수
            quant_non_empty = 0
            if quantitative_columns:
                quant_non_empty = len(df.dropna(subset=quantitative_columns))
            
            # 데이터 품질 점수
            text_completeness = round((text_non_empty / total_records) * 100, 1) if total_records > 0 else 0
            quant_completeness = round((quant_non_empty / total_records) * 100, 1) if total_records > 0 else 0
            
            # AIRISS 분석 준비도 평가
            airiss_ready = len(uid_columns) > 0 and len(opinion_columns) > 0
            hybrid_ready = len(quantitative_columns) > 0
            
            logger.info(f"📈 데이터 품질: 텍스트 {text_completeness}%, 정량 {quant_completeness}%")
            logger.info(f"🎯 분석 준비도: AIRISS={airiss_ready}, 하이브리드={hybrid_ready}")
            
        except Exception as e:
            logger.error(f"데이터 품질 분석 오류: {str(e)}")
            # 품질 분석 실패해도 업로드는 계속 진행
            total_records = len(df)
            text_completeness = 0
            quant_completeness = 0
            airiss_ready = False
            hybrid_ready = False
        
        # 🗄️ SQLiteService에 파일 데이터 저장 (🔥 수정된 부분)
        try:
            # file_data에 dataframe을 포함하여 전달
            file_data = {
                'dataframe': df,  # 🔥 핵심: DataFrame을 file_data에 포함
                'filename': file.filename,
                'file_size': len(file_contents),
                'upload_time': datetime.now(),
                'total_records': total_records,
                'column_count': len(all_columns),
                'columns': all_columns,
                'uid_columns': uid_columns,
                'opinion_columns': opinion_columns,
                'quantitative_columns': quantitative_columns,
                'text_completeness': text_completeness,
                'quant_completeness': quant_completeness,
                'airiss_ready': airiss_ready,
                'hybrid_ready': hybrid_ready,
                'file_extension': file_extension
            }
            
            # 🔥 수정된 호출: await 추가 + file_data만 전달
            file_id = await db_service.save_file(file_data)
            
            logger.info(f"💾 SQLiteService 저장 완료: {file_id}")
            
        except Exception as e:
            logger.error(f"SQLiteService 저장 오류: {str(e)}")
            logger.error(f"상세 오류: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"데이터베이스 저장 중 오류가 발생했습니다: {str(e)}")
        
        # ✅ 성공 응답 생성
        response_data = {
            "id": file_id,
            "filename": file.filename,
            "total_records": total_records,
            "column_count": len(all_columns),
            "columns": all_columns,
            "uid_columns": uid_columns,
            "opinion_columns": opinion_columns,
            "quantitative_columns": quantitative_columns,
            "airiss_ready": airiss_ready,
            "hybrid_ready": hybrid_ready,
            "data_quality": {
                "text_completeness": text_completeness,
                "quant_completeness": quant_completeness,
                "total_records": total_records,
                "text_non_empty": text_non_empty,
                "quant_non_empty": quant_non_empty
            },
            "upload_time": datetime.now().isoformat(),
            "file_size": len(file_contents),
            "message": "AIRISS v4.0 하이브리드 분석을 위한 파일 업로드가 완료되었습니다"
        }
        
        logger.info(f"🎉 파일 업로드 성공: {file.filename} -> {file_id}")
        return FileUploadResponse(**response_data)
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
        
    except Exception as e:
        # 예상치 못한 오류 처리
        logger.error(f"예상치 못한 업로드 오류: {str(e)}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        
        # 생성된 파일 ID가 있으면 정리 시도
        if file_id:
            try:
                await db_service.delete_file(file_id)
                logger.info(f"🗑️ 실패한 파일 정리 완료: {file_id}")
            except:
                pass
        
        raise HTTPException(
            status_code=500, 
            detail=f"파일 업로드 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/upload/{file_id}", response_model=FileInfoResponse)
async def get_file_info(
    file_id: str,
    db_service: SQLiteService = Depends(get_sqlite_service)
):
    """
    업로드된 파일 정보 조회
    - SQLiteService에서 파일 메타데이터 조회
    - DataFrame 기본 정보 제공
    """
    
    try:
        logger.info(f"📋 파일 정보 조회 요청: {file_id}")
        
        # 🔥 수정된 호출: await 추가
        file_record = await db_service.get_file(file_id)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # get_file에서 이미 dataframe을 포함해서 반환하므로 별도 로드 불필요
        df = file_record.get('dataframe')
        
        if df is None:
            raise HTTPException(status_code=404, detail="파일 데이터를 로드할 수 없습니다")
        
        # 실시간 데이터 상태 확인
        current_records = len(df)
        current_columns = len(df.columns)
        
        # 응답 데이터 구성
        response_data = {
            "id": file_id,
            "filename": file_record.get('filename', 'Unknown'),
            "total_records": current_records,
            "column_count": current_columns,
            "columns": [str(col) for col in df.columns.tolist()],
            "uid_columns": file_record.get('uid_columns', []),
            "opinion_columns": file_record.get('opinion_columns', []),
            "quantitative_columns": file_record.get('quantitative_columns', []),
            "upload_time": file_record.get('upload_time', datetime.now().isoformat()),
            "file_size": file_record.get('file_size', 0),
            "airiss_ready": file_record.get('airiss_ready', False),
            "hybrid_ready": file_record.get('hybrid_ready', False),
            "data_quality": {
                "text_completeness": file_record.get('text_completeness', 0),
                "quant_completeness": file_record.get('quant_completeness', 0),
                "total_records": current_records
            }
        }
        
        logger.info(f"✅ 파일 정보 조회 성공: {file_id}")
        return FileInfoResponse(**response_data)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"파일 정보 조회 오류: {str(e)}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"파일 정보 조회 중 오류가 발생했습니다: {str(e)}")

@router.delete("/upload/{file_id}")
async def delete_file(
    file_id: str,
    db_service: SQLiteService = Depends(get_sqlite_service)
):
    """
    업로드된 파일 삭제
    - SQLiteService에서 파일 및 DataFrame 데이터 완전 삭제
    """
    
    try:
        logger.info(f"🗑️ 파일 삭제 요청: {file_id}")
        
        # 파일 존재 여부 확인 (🔥 await 추가)
        file_record = await db_service.get_file(file_id)
        if not file_record:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # 파일 삭제 (🔥 await 추가)
        success = await db_service.delete_file(file_id)
        
        if success:
            logger.info(f"✅ 파일 삭제 완료: {file_id}")
            return {"message": f"파일이 성공적으로 삭제되었습니다", "file_id": file_id}
        else:
            raise HTTPException(status_code=500, detail="파일 삭제에 실패했습니다")
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"파일 삭제 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 삭제 중 오류가 발생했습니다: {str(e)}")

@router.get("/files/")
async def list_files(
    db_service: SQLiteService = Depends(get_sqlite_service)
):
    """
    업로드된 파일 목록 조회
    - 모든 업로드된 파일의 기본 정보 제공
    """
    
    try:
        logger.info("📂 파일 목록 조회 요청")
        
        # 모든 파일 목록 조회 (🔥 await 추가)
        files = await db_service.list_files()
        
        # 응답 데이터 구성
        file_list = []
        for file_record in files:
            file_info = {
                "id": file_record.get('id'),
                "filename": file_record.get('filename'),
                "total_records": file_record.get('total_records', 0),
                "upload_time": file_record.get('upload_time', ''),
                "airiss_ready": file_record.get('airiss_ready', False),
                "hybrid_ready": file_record.get('hybrid_ready', False)
            }
            file_list.append(file_info)
        
        logger.info(f"✅ 파일 목록 조회 완료: {len(file_list)}개 파일")
        return {"files": file_list, "total_count": len(file_list)}
        
    except Exception as e:
        logger.error(f"파일 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 목록 조회 중 오류가 발생했습니다: {str(e)}")
