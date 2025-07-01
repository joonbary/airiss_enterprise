# AIRISS v4.1 GitHub 저장 가이드

## 1단계: GitHub 리포지토리 생성
1. GitHub.com 접속 → New Repository
2. Repository name: `AIRISS-v4-Enhanced`
3. Description: `🤖 AI-powered Resource Intelligence Scoring System v4.1 | OK금융그룹 혁신 AI HR 시스템`
4. Private 설정 (중요!)
5. Create repository

## 2단계: 로컬 Git 초기화
```bash
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
git init
git add .
git commit -m "🚀 AIRISS v4.1 Initial Release - AI-powered HR Analytics System"
```

## 3단계: GitHub 연결
```bash
git remote add origin https://github.com/[USERNAME]/AIRISS-v4-Enhanced.git
git branch -M main
git push -u origin main
```

## 4단계: 프로젝트 문서화
- README.md 작성
- API 문서 정리
- 사용자 매뉴얼 작성

## 5단계: 지적재산권 보호
- LICENSE 파일 추가
- 저작권 명시
- 특허 출원 검토

## 주의사항
⚠️ 중요: .env 파일의 API 키 등 민감 정보는 GitHub에 업로드하지 마세요!
✅ .gitignore 파일로 보안 관리
