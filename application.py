# application.py - AWS Elastic Beanstalk 진입점
"""
AIRISS v4.1 Enhanced - AWS Elastic Beanstalk 배포용 진입점
"""

import os
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.main import app

# Elastic Beanstalk에서는 'application' 변수명이 필요
application = app

if __name__ == "__main__":
    import uvicorn
    
    # 개발 환경에서 직접 실행할 때
    uvicorn.run(
        application, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
