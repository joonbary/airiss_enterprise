# 🚀 AWS Elastic Beanstalk 배포 가이드

## 📋 왜 Elastic Beanstalk인가?
- FastAPI 애플리케이션에 최적화
- 자동 스케일링
- 로드 밸런서 제공
- 모니터링 내장
- 배포 롤백 기능

## 🎯 Step 1: application.py 생성 (EB 요구사항)
```python
# application.py (Elastic Beanstalk 진입점)
from app.main import app

# Elastic Beanstalk에서는 'application' 변수명 필요
application = app

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8000)
```

## 🎯 Step 2: requirements.txt 최적화
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
aiofiles==23.2.1
websockets==12.0
sqlite3
pandas==2.1.3
numpy==1.24.4
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
jinja2==3.1.2
matplotlib==3.7.2
seaborn==0.12.2
scikit-learn==1.3.0
```

## 🎯 Step 3: .ebextensions 설정 폴더
```yaml
# .ebextensions/01_python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application:application
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.micro
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
```

## 🎯 Step 4: EB CLI 설치 및 배포
```bash
# 1. EB CLI 설치
pip install awsebcli

# 2. EB 초기화
eb init

# 설정:
# - Application name: airiss-v4
# - Platform: Python 3.9
# - Region: ap-northeast-2 (서울)

# 3. 환경 생성 및 배포
eb create production
eb deploy

# 4. 상태 확인
eb status
eb health

# 5. 로그 확인
eb logs
```

## 🎯 Step 5: 환경 변수 설정
```bash
# AWS Console에서 설정
Environment variables:
- ENVIRONMENT=production
- DEBUG=false
- DATABASE_URL=sqlite:///./airiss_production.db
```

## 🎯 Step 6: 도메인 및 SSL
- 자동 URL: http://airiss-v4.ap-northeast-2.elasticbeanstalk.com
- 커스텀 도메인 설정 가능
- SSL 인증서 자동 제공

## 💰 비용 예상
- t3.micro 인스턴스: 월 $8.50
- 로드 밸런서: 월 $16.20
- 총 예상 비용: 월 $25-35

## 🎯 장점
✅ FastAPI에 최적화
✅ 자동 스케일링
✅ 모니터링 내장
✅ 배포 롤백 용이
✅ 프로덕션 환경에 적합
