# AIRISS AWS 배포 플랫폼 문제 해결 가이드

## 현재 상황
✅ AWS 자격 증명 성공
✅ Application "airiss-v4" 생성 완료
❌ 플랫폼 이름 오류: "Python 3.9 running on 64bit Amazon Linux 2"를 찾을 수 없음

## 🚀 즉시 해결책

### 방법 1: 사용 가능한 플랫폼 확인
```powershell
eb platform list
```

### 방법 2: 대화형 초기화 (추천)
```powershell
eb init
```

### 방법 3: 최신 Python 플랫폼 사용
```powershell
eb init --region ap-northeast-2 --platform python-3.9 airiss-v4
```

### 방법 4: 플랫폼 자동 선택
```powershell
eb init --region ap-northeast-2 airiss-v4
```

## 🎯 대화형 초기화 응답 가이드

eb init 실행 시 질문 응답:
1. Select a default region: `10) ap-northeast-2`
2. Select an application: `airiss-v4` (이미 생성됨)
3. Select a platform: `Python` 선택
4. Select a platform branch: 최신 Python 버전 선택
5. Do you wish to continue with CodeCommit?: `n`
6. Do you want to set up SSH?: `n`

## ⚡ 지금 바로 실행할 명령어

```powershell
eb init
```

이 명령어로 대화형 설정을 통해 올바른 플랫폼을 선택할 수 있습니다.
