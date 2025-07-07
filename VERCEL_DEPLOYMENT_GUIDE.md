# 🚀 AIRISS V4 - Vercel 배포 가이드

## 📋 배포 준비사항

### ✅ 사전 체크리스트
- [ ] Node.js 18+ 설치됨
- [ ] Git 설치됨  
- [ ] GitHub 계정 있음
- [ ] Vercel 계정 생성 (github.com 연동)

### 🔧 로컬 빌드 테스트
```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend
npm install
npm run build
```

## 🚀 자동 배포 실행

### Option 1: 자동화 스크립트 사용 (추천)
```bash
# 배포 스크립트 실행
C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\deploy_to_vercel.bat
```

### Option 2: 수동 실행
```bash
# 1. 배포용 폴더 생성
mkdir %USERPROFILE%\Desktop\airiss-frontend-deploy
cd %USERPROFILE%\Desktop\airiss-frontend-deploy

# 2. 파일 복사
xcopy "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend\*" . /E /H /Y

# 3. 불필요한 파일 삭제
del .env
rmdir /s /q node_modules

# 4. 의존성 설치
npm install

# 5. Git 초기화
git init
git add .
git commit -m "Initial commit: AIRISS V4 Frontend"
```

## 🐙 GitHub 저장소 생성

1. **GitHub.com** 접속
2. **New Repository** 클릭
3. 저장소 설정:
   ```
   Name: airiss-v4-frontend
   Description: AIRISS V4 AI 기반 인재 분석 시스템
   ✅ Public
   ❌ Initialize with README
   ```

4. **로컬과 연결**:
```bash
git branch -M main
git remote add origin https://github.com/[YOUR-USERNAME]/airiss-v4-frontend.git
git push -u origin main
```

## 🔥 Vercel 배포

### 1. Vercel 연동
1. **[vercel.com](https://vercel.com)** 접속
2. **"Sign Up"** → **"Continue with GitHub"**
3. GitHub 권한 승인

### 2. 프로젝트 배포  
1. **"New Project"** 클릭
2. GitHub에서 `airiss-v4-frontend` 선택
3. **"Import"** 클릭
4. 설정 확인 후 **"Deploy"** 클릭

### 3. 환경 변수 설정
**Vercel 프로젝트 → Settings → Environment Variables**

```bash
REACT_APP_API_URL=https://your-backend-api.herokuapp.com
REACT_APP_WS_URL=wss://your-backend-api.herokuapp.com/ws
REACT_APP_ENVIRONMENT=production
REACT_APP_DEBUG=false
```

## 🔄 자동 배포 활용

### 코드 수정 후 배포
```bash
git add .
git commit -m "✨ 새로운 기능 추가"
git push origin main
# → 자동으로 Vercel에 배포됨!
```

### 브랜치별 미리보기
```bash
git checkout -b develop
git push origin develop
# → Vercel이 미리보기 URL 생성
```

## 📱 배포 후 확인사항

### ✅ 기능 테스트
- [ ] 메인 페이지 로딩
- [ ] 라우팅 동작 (/dashboard, /upload, /analysis)
- [ ] 반응형 디자인 (모바일)
- [ ] 콘솔 에러 없음

### 📊 성능 테스트
- Chrome DevTools → Lighthouse
- 목표: Performance 80+ 점수

## 🌐 배포 결과

```
✅ 프론트엔드: https://airiss-v4-frontend.vercel.app
❌ 백엔드: 아직 미배포 (localhost:8002)
```

## 📞 문제 해결

### 빌드 실패 시
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### API 연결 실패 시
- 환경 변수 `REACT_APP_API_URL` 확인
- 백엔드 서버 배포 필요
- CORS 설정 확인

### Vercel 배포 실패 시
- GitHub 저장소 public 확인
- vercel.json 문법 확인
- 빌드 로그에서 에러 확인

## 🎯 다음 단계

1. **백엔드 배포** - Railway/Render 추천
2. **도메인 연결** - 커스텀 도메인 설정
3. **성능 최적화** - Code Splitting, PWA
4. **모니터링** - Vercel Analytics 설정

---

**🎉 축하합니다! AIRISS V4가 성공적으로 배포되었습니다!**
