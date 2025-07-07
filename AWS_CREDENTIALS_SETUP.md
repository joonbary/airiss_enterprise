# 🔑 AWS 자격 증명 설정 가이드

## 현재 문제
```
ERROR: The security token included in the request is invalid.
You have not yet set up your credentials or your credentials are incorrect
```

## 🚀 해결 단계

### 1단계: AWS 자격 증명 설정
```powershell
aws configure
```

### 입력할 정보 (AWS 콘솔에서 확인):

1. **AWS Access Key ID**: 
   - AWS 콘솔 → IAM → 사용자 → 보안 자격 증명 → 액세스 키 만들기

2. **AWS Secret Access Key**: 
   - 위와 동일한 곳에서 확인

3. **Default region name**: 
   ```
   ap-northeast-2
   ```

4. **Default output format**: 
   ```
   json
   ```

### 2단계: 설정 확인
```powershell
aws sts get-caller-identity
```

### 3단계: EB 초기화 재시도
```powershell
eb init --region ap-northeast-2 --platform "Python 3.9 running on 64bit Amazon Linux 2" airiss-v4
```

---

## 🔧 AWS 콘솔에서 액세스 키 생성 방법

### 방법 1: 새 액세스 키 생성
1. AWS 콘솔 로그인
2. IAM → 사용자 → [본인 사용자명] 클릭
3. "보안 자격 증명" 탭
4. "액세스 키 만들기" 버튼 클릭
5. "Command Line Interface (CLI)" 선택
6. 생성된 키 정보 복사

### 방법 2: 기존 키 사용 (이미 있는 경우)
- 기존에 만들어둔 액세스 키가 있다면 그것 사용

---

## ⚠️ 필요한 IAM 권한

다음 권한이 필요합니다:
- `ElasticBeanstalkFullAccess`
- `IAMReadOnlyAccess`
- `EC2ReadOnlyAccess`

권한 확인 방법:
1. AWS 콘솔 → IAM → 사용자
2. 본인 사용자 선택
3. "권한" 탭에서 위 권한들 확인

---

## 🚨 만약 AWS 계정이 없다면...

1. AWS 회원가입: https://aws.amazon.com/ko/
2. 프리티어 계정 생성
3. IAM 사용자 생성 및 권한 부여

---

## ✅ 성공 확인

설정이 완료되면 다음 명령어가 정상 실행되어야 합니다:
```powershell
aws sts get-caller-identity
```

결과 예시:
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012", 
    "Arn": "arn:aws:iam::123456789012:user/DevAdmin"
}
```
