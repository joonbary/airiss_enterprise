import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"Created: {path}")

# 1. Upload 엔드포인트
upload_endpoint = """from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import pandas as pd
import io
import uuid
from datetime import datetime
import logging
import os

from app.db.database import get_db
from app.models.file import FileRecord
from app.schemas.upload import UploadResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    \"\"\"파일 업로드 및 기초 분석\"\"\"
    try:
        logger.info(f"AIRISS v4.0 파일 업로드 시작: {file.filename}")
        
        # 파일 확장자 확인
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="지원되지 않는 파일 형식입니다. CSV 또는 Excel 파일만 가능합니다.")
        
        # 파일 내용 읽기
        contents = await file.read()
        
        # 파일 타입에 따라 DataFrame 생성
        df = None
        if file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
            logger.info("Excel 파일 처리 완료")
        elif file.filename.endswith('.csv'):
            # 여러 인코딩 시도
            encodings = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']
            for encoding in encodings:
                try:
                    df = pd.read_csv(io.StringIO(contents.decode(encoding)))
                    logger.info(f"CSV 파일 처리 완료 (인코딩: {encoding})")
                    break
                except:
                    continue
            
            if df is None:
                raise HTTPException(status_code=400, detail="CSV 파일 인코딩을 인식할 수 없습니다")
        
        # 컬럼 분석
        all_columns = list(df.columns)
        
        # UID 컬럼 감지
        uid_keywords = ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp']
        uid_columns = [col for col in all_columns if any(keyword in col.lower() for keyword in uid_keywords)]
        
        # 의견 컬럼 감지
        opinion_keywords = ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', '피드백', 'comment', 'review']
        opinion_columns = [col for col in all_columns if any(keyword in col.lower() for keyword in opinion_keywords)]
        
        # 정량데이터 컬럼 감지
        quant_keywords = ['점수', 'score', '평점', 'rating', '등급', 'grade', 'level', '달성률', '비율', 'rate', '%', 'percent']
        quantitative_columns = []
        
        for col in all_columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in quant_keywords):
                # 실제 데이터 확인
                sample_data = df[col].dropna().head(10)
                if len(sample_data) > 0:
                    # 정량적 데이터인지 확인
                    is_quantitative = True
                    quantitative_columns.append(col)
        
        # 데이터베이스에 저장
        file_id = str(uuid.uuid4())
        file_record = FileRecord(
            id=file_id,
            filename=file.filename,
            upload_time=datetime.utcnow(),
            total_records=len(df),
            column_count=len(all_columns),
            status="uploaded",
            metadata={
                "uid_columns": uid_columns,
                "opinion_columns": opinion_columns,
                "quantitative_columns": quantitative_columns
            }
        )
        db.add(file_record)
        db.commit()
        
        # DataFrame을 임시 파일로 저장
        os.makedirs('temp_data', exist_ok=True)
        df.to_pickle(f'temp_data/{file_id}.pkl')
        
        logger.info(f"파일 저장 완료: {file_id}")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "total_records": len(df),
            "column_count": len(all_columns),
            "uid_columns": uid_columns,
            "opinion_columns": opinion_columns,
            "quantitative_columns": quantitative_columns,
            "airiss_ready": len(uid_columns) > 0 and len(opinion_columns) > 0,
            "hybrid_ready": len(quantitative_columns) > 0,
            "data_quality": {
                "non_empty_records": len(df.dropna()),
                "completeness": round((len(df.dropna()) / len(df)) * 100, 1) if len(df) > 0 else 0,
                "quantitative_completeness": round((len(quantitative_columns) / len(all_columns)) * 100, 1) if len(all_columns) > 0 else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 업로드 오류: {e}")
        raise HTTPException(status_code=400, detail=f"파일 처리 오류: {str(e)}")
"""
create_file('app/api/v1/endpoints/upload.py', upload_endpoint)

# 2. endpoints __init__.py
endpoints_init = """# API v1 endpoints
"""
create_file('app/api/v1/endpoints/__init__.py', endpoints_init)

# 3. 업데이트된 API 라우터
updated_api_router = """from fastapi import APIRouter

from app.api.v1.endpoints import upload

api_router = APIRouter()

# 엔드포인트 라우터 포함
api_router.include_router(upload.router, tags=["upload"])

# 테스트 엔드포인트
@api_router.get("/test")
async def test_endpoint():
    return {"message": "API v1 is working"}
"""
create_file('app/api/v1/api.py', updated_api_router)

print("\n✅ Upload 엔드포인트가 추가되었습니다.")
print("\n서버를 재시작하고 http://localhost:8001/docs 에서 확인하세요.")