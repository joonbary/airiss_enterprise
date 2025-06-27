"""
임시 데이터 저장소
실제 프로덕션에서는 Redis 또는 S3 사용 권장
"""
import pandas as pd
from typing import Dict, Optional

# 메모리 저장소 (개발용)
_dataframe_store: Dict[str, pd.DataFrame] = {}

def store_dataframe(file_id: str, df: pd.DataFrame) -> None:
    """DataFrame 저장"""
    _dataframe_store[file_id] = df

def get_dataframe(file_id: str) -> Optional[pd.DataFrame]:
    """DataFrame 조회"""
    return _dataframe_store.get(file_id)

def delete_dataframe(file_id: str) -> None:
    """DataFrame 삭제"""
    if file_id in _dataframe_store:
        del _dataframe_store[file_id]

def clear_all() -> None:
    """모든 데이터 삭제"""
    _dataframe_store.clear()