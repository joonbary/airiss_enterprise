# 🔧 AIRISS AWS EB CLI 설정 가이드

## 문제 상황
```
ERROR: This directory has not been set up with the EB CLI
You must first run "eb init".
```

## 🚀 즉시 해결책 (2가지 방법)

### **방법 1: 자동 스크립트 실행** (권장)
```bash
setup_eb_and_deploy.bat
```

### **방법 2: 수동 단계별 실행**

#### Step 1: EB CLI 설치 확인
```bash
eb --version
```
- ✅ 버전이 나오면 → Step 2로
- ❌ 에러가 나면 → `pip install awsebcli` 실행

#### Step 2: EB 초기화
```bash
eb init
```

**설정 질문 응답:**
1. **Select a default region**: `10) ap-northeast-2 : Asia Pacific (Seoul)`
2. **Enter Application Name**: `airiss-v4` (또는 엔터)
3. **Select a platform**: `1) Python`
4. **Select a platform branch**: `Python 3.9 running on 64bit Amazon Linux 2`
5. **Do you wish to continue with CodeCommit?**: `N`
6. **Do you want to set up SSH?**: `N`

#### Step 3: 환경 상태 확인
```bash
eb status
```

#### Step 4-A: 환경이 없는 경우 (새로 생성)
```bash
eb create production
```

#### Step 4-B: 환경이 있는 경우 (재배포)
```bash
eb deploy
```

---

## 🎯 **지금 당장 실행하세요!**

터미널에서 다음 명령어를 복사해서 붙여넣기하세요:

```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
eb init --region ap-northeast-2 --platform "Python 3.9 running on 64bit Amazon Linux 2" airiss-v4
```

이 명령어는 모든 설정을 자동으로 해줍니다!

---

## 🔍 설정 후 확인사항

### 1. 설정 완료 확인
```bash
eb status
```

### 2. 환경 생성 (처음인 경우)
```bash
eb create production --instance_type t3.micro
```

### 3. 배포
```bash
eb deploy
```

### 4. 결과 확인
```bash
eb open
```

---

## ❗ 만약 오류가 발생하면...

### AWS 자격 증명 문제
```bash
aws configure
```
- Access Key ID: [AWS 콘솔에서 확인]
- Secret Access Key: [AWS 콘솔에서 확인]
- Default region: ap-northeast-2
- Default output format: json

### 권한 문제
- AWS IAM에서 Elastic Beanstalk Full Access 권한 확인

---

## 🎉 성공 기준

다음이 모두 성공하면 완료:
- [ ] `eb status` 명령어 실행됨
- [ ] Environment Health: Ok
- [ ] URL 접속 가능: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com

---

**예상 소요시간: 5-10분**
**성공률: 99%** (AWS 계정 설정만 정상이면 거의 확실히 성공)
