# Amplify FastAPI 빌드 설정 수정 가이드

## 🎯 문제: Amplify가 정적 사이트로 인식

현재 Amplify는 AIRISS를 정적 웹사이트로 배포했지만, 
FastAPI는 Python 서버가 필요합니다.

## 🔧 해결 방법: 빌드 설정 변경

### 1. AWS Amplify Console에서 설정 변경

1. **AWS Amplify Console** → **airiss_enterprise** 클릭
2. **"Build settings"** 탭 클릭
3. **"Edit"** 버튼 클릭
4. **빌드 설정을 다음으로 교체**:

```yaml
version: 1
backend:
  phases:
    preBuild:
      commands:
        - echo "Installing Python and dependencies..."
        - yum install -y python3 python3-pip
        - python3 -m pip install --upgrade pip
        - pip3 install -r requirements.txt
    build:
      commands:
        - echo "Starting FastAPI application..."
        - python3 init_database.py
        - echo "Database initialized"
    postBuild:
      commands:
        - echo "Starting server..."
        - nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        - sleep 5
frontend:
  phases:
    preBuild:
      commands:
        - echo "No frontend build needed"
    build:
      commands:
        - echo "Copying static files..."
        - cp -r app/static/* ./ || echo "No static files"
        - cp -r app/templates/* ./ || echo "No templates"
  artifacts:
    baseDirectory: /
    files:
      - '**/*'
```

### 2. 환경 변수 추가

**"Environment variables"** 섹션에 추가:
```
PORT=8000
PYTHONPATH=/var/app/current
ENVIRONMENT=production
```

### 3. 재배포 실행

**"Save and deploy"** 클릭

## ⚠️ 한계사항

Amplify는 정적 호스팅에 최적화되어 있어서 
FastAPI 같은 서버 애플리케이션에는 제한이 있습니다.

**권장**: Elastic Beanstalk로 이전
