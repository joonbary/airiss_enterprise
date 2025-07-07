# app/db/sqlite_service.py - Job ID 불일치 완전 해결 버전
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
    
    def __init__(self, db_path: str = "C:/AIRISS/airiss.db"):
        self.db_path = db_path
        
    async def get_connection(self):
        """aiosqlite 연결 객체 반환 (with/as에서 사용 가능)"""
        return await aiosqlite.connect(self.db_path)

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

    # 🔥 핵심 수정: Job ID 불일치 완전 해결
    async def create_analysis_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 생성 (Analysis API 전용) - Job ID 불일치 완전 해결"""
        try:
            # 🔥 1단계: 전달받은 job_id를 절대적으로 사용
            if 'job_id' in job_data and job_data['job_id']:
                job_id = str(job_data['job_id'])
                logger.debug(f"🎯 전달받은 job_id 사용: {job_id}")
            else:
                # job_id가 없을 경우만 새로 생성
                job_id = str(uuid.uuid4())
                job_data['job_id'] = job_id
                logger.debug(f"🆕 새로운 job_id 생성: {job_id}")
            
            # 🔥 2단계: status 필드 기본값 설정
            if 'status' not in job_data:
                job_data['status'] = 'created'
            
            # 🔥 3단계: 중복 검사 (선택적)
            async with aiosqlite.connect(self.db_path) as db:
                # 기존 job_id 확인
                async with db.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)) as cursor:
                    existing = await cursor.fetchone()
                    if existing:
                        error_msg = f"❌ 중복된 job_id: {job_id}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                
                # 🔥 4단계: DB에 저장 (job_id를 id 컬럼에 직접 저장)
                await db.execute("""
                    INSERT INTO jobs (
                        id, file_id, status, created_at, updated_at, job_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    job_id,  # 🔥 핵심: 전달받은 job_id를 id로 저장
                    job_data['file_id'],
                    job_data['status'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    json.dumps(job_data)
                ))
                await db.commit()
            
            logger.info(f"✅ 분석 작업 생성 완료: {job_id}")
            
            # 🔥 5단계: 검증 - 저장된 ID와 요청한 ID가 정확히 일치하는지 확인
            verification = await self.get_analysis_job(job_id)
            if not verification:
                raise ValueError(f"저장 검증 실패: {job_id}")
            
            # 🔥 6단계: 최종 반환 (절대적으로 동일한 ID 반환)
            return str(job_id)
            
        except Exception as e:
            logger.error(f"❌ 분석 작업 생성 오류: {e}")
            logger.error(f"오류 상세: {traceback.format_exc()}")
            raise

    async def get_analysis_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """분석 작업 조회 (Analysis API 호환)"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, file_id, status, created_at, updated_at, job_data
                    FROM jobs WHERE id = ?
                """, (job_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        logger.warning(f"작업을 찾을 수 없음: {job_id}")
                        return None
                    
                    job_data = json.loads(row[5])
                    
                    # 🔥 핵심: DB의 id 컬럼값을 job_id로 설정
                    job_data.update({
                        'job_id': row[0],  # 🔥 DB의 id를 job_id로 사용
                        'file_id': row[1],
                        'status': row[2],
                        'created_at': row[3],
                        'updated_at': row[4]
                    })
                    
                    return job_data
                    
        except Exception as e:
            logger.error(f"❌ 분석 작업 조회 오류: {e}")
            return None

    async def update_analysis_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """분석 작업 업데이트 (Analysis API 호환) - job_data 병합 보장"""
        try:
            # 기존 job_data만 불러오기
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT job_data FROM jobs WHERE id = ?", (job_id,)) as cursor:
                    row = await cursor.fetchone()
                    job_data = json.loads(row[0]) if row and row[0] else {}

            # job_data에 업데이트 병합
            job_data.update(updates)
            job_data['updated_at'] = datetime.now().isoformat()
            # 상태 필드는 별도 관리
            status = job_data.get('status', updates.get('status', 'completed'))

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE jobs 
                    SET status = ?, updated_at = ?, job_data = ?
                    WHERE id = ?
                """, (
                    status,
                    job_data['updated_at'],
                    json.dumps(job_data),
                    job_id
                ))
                await db.commit()
            logger.debug(f"✅ 분석 작업 업데이트 완료: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 분석 작업 업데이트 오류: {e}")
            return False

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
                            'end_time': job_data.get('end_time', ''),
                            'average_score': job_data.get('average_score', 0),
                            'enable_ai_feedback': job_data.get('enable_ai_feedback', False)
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

    # 🔥 레거시 메서드들 (하위 호환성)
    async def save_job(self, job_data: Dict[str, Any]) -> str:
        """레거시 호환성을 위한 메서드 - create_analysis_job를 호출"""
        logger.warning("save_job은 deprecated됩니다. create_analysis_job을 사용하세요.")
        return await self.create_analysis_job(job_data)
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """레거시 호환성을 위한 메서드 - get_analysis_job을 호출"""
        logger.warning("get_job은 deprecated됩니다. get_analysis_job을 사용하세요.")
        return await self.get_analysis_job(job_id)
    
    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """레거시 호환성을 위한 메서드 - update_analysis_job을 호출"""
        logger.warning("update_job은 deprecated됩니다. update_analysis_job을 사용하세요.")
        return await self.update_analysis_job(job_id, updates)

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
                            'analysis_mode': job_data.get('analysis_mode', 'hybrid'),
                            'enable_ai_feedback': job_data.get('enable_ai_feedback', False)
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

# 인스턴스 생성 및 export
sqlite_service = SQLiteService()