# 🚀 AWS Amplify 배포 가이드

## 📋 준비사항
1. AWS 계정 (console.aws.amazon.com)
2. GitHub에 코드 업로드 완료
3. 신용카드 등록 (프리 티어 사용 시 무료)

## 🎯 Step 1: AWS Amplify 서비스 선택
1. console.aws.amazon.com 로그인
2. 서비스 검색에서 "Amplify" 입력
3. "AWS Amplify" 클릭

## 🎯 Step 2: 앱 생성
1. "Create new app" 클릭
2. "Host web app" 선택
3. "GitHub" 선택
4. GitHub 계정 연결 승인

## 🎯 Step 3: Repository 연결
1. "airiss_enterprise" repository 선택
2. Branch: "main" 선택
3. "Next" 클릭

## 🎯 Step 4: 빌드 설정
App name: AIRISS-v4-Production
Environment: production

Build settings:
```yaml
version: 1
applications:
  - frontend:
      phases:
        preBuild:
          commands:
            - echo "Installing Python dependencies..."
            - pip install -r requirements.txt
        build:
          commands:
            - echo "Building AIRISS v4..."
            - python init_database.py
      artifacts:
        baseDirectory: /
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
    appRoot: /
```

## 🎯 Step 5: 검토 및 배포
1. 설정 검토
2. "Save and deploy" 클릭
3. 배포 완료 대기 (5-10분)

## 🎯 Step 6: 결과 확인
- 배포 URL: https://YOUR-APP-ID.amplifyapp.com
- 커스텀 도메인 설정 가능
- SSL 인증서 자동 제공
- GitHub 푸시 시 자동 재배포

## 💰 비용
- 프리 티어: 월 1,000 빌드 분 무료
- 호스팅: 월 5GB 무료
- 예상 비용: 월 $0-10 (소규모 사용 시)
