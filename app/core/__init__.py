# Core Services Package
"""
AIRISS v4.0 Core 모듈
- WebSocket 연결 관리
- 분석 엔진
- 프레임워크 정의
"""

# ConnectionManager를 직접 export
from .websocket_manager import ConnectionManager

# 기타 핵심 클래스들도 export (필요한 경우)
try:
    from .airiss_analyzer import AIRISSHybridAnalyzer
    from .airiss_framework import AIRISS_FRAMEWORK
except ImportError:
    # 선택적 import (missing dependency 대응)
    pass

__all__ = [
    'ConnectionManager',
    'AIRISSHybridAnalyzer', 
    'AIRISS_FRAMEWORK'
]