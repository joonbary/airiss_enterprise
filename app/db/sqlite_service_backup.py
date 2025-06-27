# app/db/sqlite_service.py - 완전한 수정 버전
import aiosqlite
import pickle
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteService:
    """SQLite 데이터베이스 서비스 클래스"""
    
    def __init__(self, db_path: str = "airiss.db"):
        self.db_path = db_path
        
    async def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Files 테이블
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS files (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        upload_time TIMESTAMP NOT NULL,
                        total_records INTEGER NOT NULL,
                        columns TEXT NOT NULL,
                        uid_columns TEXT NOT NULL,
                        opinion_columns TEXT NOT NULL,
                        quantitative_columns TEXT NOT NULL,
                        file_data BLOB NOT NULL
                    )
                """)
                
                # Jobs 테이블
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        file_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        job_data TEXT NOT NULL,
                        FOREIGN KEY (file_id) REFERENCES files (id)
                    )
                """)
                
                # Results 테이블
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS results (
                        id TEXT PRIMARY KEY,
                        job_id TEXT NOT NULL,
                        uid TEXT NOT NULL,
                        result_data TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (job_id) REFERENCES jobs (id)
                    )
                """)
                
                await db.commit()
                logger.info("✅ SQLite 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 오류: {e}")
            raise

    async def save_file(self, file_data: Dict[str, Any]) -> str:
        """파일 정보를 데이터베이스에 저장"""
        try:
            file_id = str(uuid.uuid4())
            
            # DataFrame을 pickle로 직렬화
            df = file_data['dataframe']
            file_data_blob = pickle.dumps(df)
            
            # 데이터베이스 스키마에 맞는 구조로 저장
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO files (
                        id, filename, upload_time, total_records, 
                        columns, uid_columns, opinion_columns, 
                        quantitative_columns, file_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id,
                    file_data['filename'],
                    datetime.now().isoformat(),
                    file_data['total_records'],
                    json.dumps(file_data['columns']),
                    json.dumps(file_data['uid_columns']),
                    json.dumps(file_data['opinion_columns']),
                    json.dumps(file_data.get('quantitative_columns', [])),
                    file_data_blob
                ))
                await db.commit()
            
            logger.info(f"✅ 파일 저장 완료: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 오류: {e}")
            raise

    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 정보를 데이터베이스에서 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, filename, upload_time, total_records,
                           columns, uid_columns, opinion_columns,
                           quantitative_columns, file_data
                    FROM files WHERE id = ?
                """, (file_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    # bytes 변환 처리
                    file_data_blob = row[8]
                    if isinstance(file_data_blob, str):
                        # string인 경우 bytes로 변환
                        file_data_blob = file_data_blob.encode('latin1')
                    
                    # DataFrame 복원
                    df = pickle.loads(file_data_blob)
                    
                    return {
                        'id': row[0],
                        'filename': row[1],
                        'upload_time': row[2],
                        'total_records': row[3],
                        'columns': json.loads(row[4]),
                        'uid_columns': json.loads(row[5]),
                        'opinion_columns': json.loads(row[6]),
                        'quantitative_columns': json.loads(row[7]),
                        'dataframe': df
                    }
                    
        except Exception as e:
            logger.error(f"❌ 파일 조회 오류: {e}")
            raise

    async def delete_file(self, file_id: str) -> bool:
        """파일을 데이터베이스에서 삭제"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 관련 작업들도 함께 삭제
                await db.execute("DELETE FROM results WHERE job_id IN (SELECT id FROM jobs WHERE file_id = ?)", (file_id,))
                await db.execute("DELETE FROM jobs WHERE file_id = ?", (file_id,))
                await db.execute("DELETE FROM files WHERE id = ?", (file_id,))
                await db.commit()
                
                logger.info(f"✅ 파일 삭제 완료: {file_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 파일 삭제 오류: {e}")
            return False

    async def list_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """파일 목록 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, filename, upload_time, total_records
                    FROM files 
                    ORDER BY upload_time DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        {
                            'id': row[0],
                            'filename': row[1],
                            'upload_time': row[2],
                            'total_records': row[3]
                        }
                        for row in rows
                    ]
                    
        except Exception as e:
            logger.error(f"❌ 파일 목록 조회 오류: {e}")
            return []

    async def save_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 정보를 데이터베이스에 저장"""
        try:
            # 🔥 핵심 수정 강화: job_data에 있는 job_id를 절대적으로 우선 사용
            if 'job_id' in job_data and job_data['job_id']:
                job_id = str(job_data['job_id'])  # 문자열로 변환하여 확실히 처리
                logger.debug(f"기존 job_id 사용: {job_id}")
            else:
                job_id = str(uuid.uuid4())
                job_data['job_id'] = job_id
                logger.debug(f"새로운 job_id 생성: {job_id}")
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO jobs (
                        id, file_id, status, created_at, updated_at, job_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    job_id,
                    job_data['file_id'],
                    job_data['status'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    json.dumps(job_data)
                ))
                await db.commit()
            
            logger.info(f"✅ 작업 저장 완료: {job_id}")
            # 🔥 반환값 확인: 저장한 job_id와 정확히 동일한 값 반환
            return str(job_id)
            
        except Exception as e:
            logger.error(f"❌ 작업 저장 오류: {e}")
            raise

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """분석 작업 정보를 데이터베이스에서 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, file_id, status, created_at, updated_at, job_data
                    FROM jobs WHERE id = ?
                """, (job_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    job_data = json.loads(row[5])
                    job_data.update({
                        'id': row[0],
                        'file_id': row[1],
                        'status': row[2],
                        'created_at': row[3],
                        'updated_at': row[4]
                    })
                    
                    return job_data
                    
        except Exception as e:
            logger.error(f"❌ 작업 조회 오류: {e}")
            return None

    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """분석 작업 정보 업데이트"""
        try:
            # 기존 작업 정보 조회
            existing_job = await self.get_job(job_id)
            if not existing_job:
                return False
            
            # 업데이트된 데이터 병합
            existing_job.update(updates)
            existing_job['updated_at'] = datetime.now().isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE jobs 
                    SET status = ?, updated_at = ?, job_data = ?
                    WHERE id = ?
                """, (
                    existing_job['status'],
                    existing_job['updated_at'],
                    json.dumps(existing_job),
                    job_id
                ))
                await db.commit()
            
            logger.debug(f"✅ 작업 업데이트 완료: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 작업 업데이트 오류: {e}")
            return False

    async def list_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """분석 작업 목록 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT j.id, j.file_id, j.status, j.created_at, j.updated_at, 
                           f.filename, j.job_data
                    FROM jobs j
                    LEFT JOIN files f ON j.file_id = f.id
                    ORDER BY j.created_at DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    jobs = []
                    for row in rows:
                        job_data = json.loads(row[6])
                        jobs.append({
                            'id': row[0],
                            'file_id': row[1],
                            'status': row[2],
                            'created_at': row[3],
                            'updated_at': row[4],
                            'filename': row[5],
                            'total_records': job_data.get('total_records', 0),
                            'processed_records': job_data.get('processed', 0),
                            'analysis_mode': job_data.get('analysis_mode', 'hybrid')
                        })
                    
                    return jobs
                    
        except Exception as e:
            logger.error(f"❌ 작업 목록 조회 오류: {e}")
            return []

    async def save_results(self, job_id: str, results: List[Dict[str, Any]]) -> bool:
        """분석 결과를 데이터베이스에 저장"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for result in results:
                    result_id = str(uuid.uuid4())
                    await db.execute("""
                        INSERT INTO results (
                            id, job_id, uid, result_data, created_at
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        result_id,
                        job_id,
                        result.get('uid', 'unknown'),
                        json.dumps(result),
                        datetime.now().isoformat()
                    ))
                
                await db.commit()
                logger.info(f"✅ 결과 저장 완료: {job_id} ({len(results)}개)")
                return True
                
        except Exception as e:
            logger.error(f"❌ 결과 저장 오류: {e}")
            return False

    async def get_results(self, job_id: str) -> List[Dict[str, Any]]:
        """분석 결과 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT uid, result_data, created_at
                    FROM results 
                    WHERE job_id = ?
                    ORDER BY created_at
                """, (job_id,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        {
                            'uid': row[0],
                            'created_at': row[2],
                            **json.loads(row[1])
                        }
                        for row in rows
                    ]
                    
        except Exception as e:
            logger.error(f"❌ 결과 조회 오류: {e}")
            return []

    async def get_database_stats(self) -> Dict[str, Any]:
        """데이터베이스 통계 정보 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 파일 수
                async with db.execute("SELECT COUNT(*) FROM files") as cursor:
                    files_count = (await cursor.fetchone())[0]
                
                # 작업 수
                async with db.execute("SELECT COUNT(*) FROM jobs") as cursor:
                    jobs_count = (await cursor.fetchone())[0]
                
                # 결과 수
                async with db.execute("SELECT COUNT(*) FROM results") as cursor:
                    results_count = (await cursor.fetchone())[0]
                
                return {
                    'files_count': files_count,
                    'jobs_count': jobs_count,
                    'results_count': results_count,
                    'db_path': self.db_path
                }
                
        except Exception as e:
            logger.error(f"❌ 통계 조회 오류: {e}")
            return {}

    async def cleanup_old_data(self, days: int = 30) -> bool:
        """오래된 데이터 정리 (기본 30일 이상)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                # 오래된 결과 삭제
                await db.execute("DELETE FROM results WHERE created_at < ?", (cutoff_str,))
                
                # 완료된 작업 중 오래된 것들 삭제
                await db.execute("""
                    DELETE FROM jobs 
                    WHERE status IN ('completed', 'failed') 
                    AND updated_at < ?
                """, (cutoff_str,))
                
                await db.commit()
                logger.info(f"✅ 오래된 데이터 정리 완료: {days}일 이전")
                return True
                
        except Exception as e:
            logger.error(f"❌ 데이터 정리 오류: {e}")
            return False

    # 🆕 Analysis API 호환성 메서드들
    async def create_analysis_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 생성 (Analysis API 호환)"""
        # status 필드가 없으면 기본값 설정
        if 'status' not in job_data:
            job_data['status'] = 'created'
        
        return await self.save_job(job_data)
    
    async def get_analysis_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """분석 작업 조회 (Analysis API 호환)"""
        return await self.get_job(job_id)
    
    async def update_analysis_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """분석 작업 업데이트 (Analysis API 호환)"""
        return await self.update_job(job_id, updates)
    
    async def get_completed_analysis_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """완료된 분석 작업 목록 조회"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT j.id, j.file_id, j.status, j.created_at, j.updated_at, 
                           f.filename, j.job_data
                    FROM jobs j
                    LEFT JOIN files f ON j.file_id = f.id
                    WHERE j.status = 'completed'
                    ORDER BY j.updated_at DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    jobs = []
                    for row in rows:
                        job_data = json.loads(row[6])
                        jobs.append({
                            'job_id': row[0],
                            'file_id': row[1],
                            'status': row[2],
                            'created_at': row[3],
                            'updated_at': row[4],
                            'filename': row[5],
                            'processed_records': job_data.get('processed_records', 0),
                            'total_records': job_data.get('total_records', 0),
                            'analysis_mode': job_data.get('analysis_mode', 'hybrid'),
                            'end_time': job_data.get('end_time', '')
                        })
                    
                    return jobs
                    
        except Exception as e:
            logger.error(f"❌ 완료된 작업 목록 조회 오류: {e}")
            return []
    
    async def save_analysis_result(self, job_id: str, uid: str, result_data: Dict[str, Any]) -> bool:
        """개별 분석 결과 저장"""
        try:
            result_id = str(uuid.uuid4())
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO results (
                        id, job_id, uid, result_data, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    result_id,
                    job_id,
                    uid,
                    json.dumps(result_data),
                    datetime.now().isoformat()
                ))
                await db.commit()
            
            logger.debug(f"✅ 개별 결과 저장: {job_id} - {uid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 개별 결과 저장 오류: {e}")
            return False
    
    async def get_analysis_results(self, job_id: str) -> List[Dict[str, Any]]:
        """분석 결과 조회 (Analysis API 호환)"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT uid, result_data, created_at
                    FROM results 
                    WHERE job_id = ?
                    ORDER BY created_at
                """, (job_id,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        {
                            'uid': row[0],
                            'result_data': json.loads(row[1]),
                            'created_at': row[2]
                        }
                        for row in rows
                    ]
                    
        except Exception as e:
            logger.error(f"❌ 분석 결과 조회 오류: {e}")
            return []

# 인스턴스 생성 및 export
sqlite_service = SQLiteService()