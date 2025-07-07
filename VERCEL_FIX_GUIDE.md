# AIRISS v4.1 Vercel 배포 문제 해결 가이드

## 🚨 현재 문제
- Vercel 배포 성공하지만 static 파일 로딩 실패
- ERR_HTTP2_PROTOCOL_ERROR
- 폰트, manifest, favicon 파일 404 오류

## 🔧 해결 방법 (우선순위별)

### 1️⃣ 즉시 시도 (가장 쉬운 방법)
```bash
# 1. 배치 스크립트 실행
quick_redeploy.bat

# 2. 수동 실행시
cd airiss-v4-frontend
npm run build
git add .
git commit -m "Fix static files serving"
git push origin main
```

### 2️⃣ vercel.json 수정 완료 ✅
- MIME type 명시적 설정
- CORS 헤더 추가
- 캐시 최적화

### 3️⃣ 문제 지속시 대안책

#### A. 폰트 CDN 사용
`src/index.tsx`에 추가:
```typescript
import InlineFonts from './InlineFonts';

// App 컴포넌트 최상단에 추가
<InlineFonts />
```

#### B. Netlify 배포 고려
```bash
# Netlify CLI 설치
npm install -g netlify-cli

# 배포
cd build
netlify deploy --prod --dir .
```

#### C. GitHub Pages 배포
```bash
npm install --save-dev gh-pages

# package.json에 추가
"homepage": "https://joonbary.github.io/airiss-enterprise",
"scripts": {
  "predeploy": "npm run build",
  "deploy": "gh-pages -d build"
}

npm run deploy
```

## ⏱️ 예상 해결 시간
- vercel.json 수정: 5분
- 폰트 CDN 대안: 10분  
- 호스팅 변경: 30분

## 🎯 성공 확인 방법
1. https://airiss-enterprise-v4.vercel.app 접속
2. 브라우저 개발자도구 (F12) 확인
3. Console에 오류 없음
4. 폰트가 정상적으로 로딩됨

## 📞 추가 지원
- 문제 지속시 Slack/이메일로 연락
- 스크린샷과 함께 오류 내용 공유
