# Contributing to AIRISS 🤝

AIRISS 프로젝트에 기여해주셔서 감사합니다! 

이 문서는 효과적이고 일관된 기여를 위한 가이드라인을 제공합니다.

---

## 🎯 기여 방법

### 1️⃣ **이슈 보고**
- 버그를 발견했거나 새로운 기능을 제안하고 싶다면 [GitHub Issues](https://github.com/joonbary/airiss_enterprise/issues)를 이용하세요
- 이슈 템플릿을 따라 작성해주세요
- 중복 이슈가 없는지 먼저 확인해주세요

### 2️⃣ **코드 기여**
1. 저장소를 포크합니다
2. 새로운 브랜치를 생성합니다: `git checkout -b feature/새기능`
3. 변경사항을 커밋합니다: `git commit -m "feat: 새로운 기능 추가"`
4. 브랜치에 푸시합니다: `git push origin feature/새기능`
5. Pull Request를 생성합니다

---

## 📝 **코딩 스타일**

### Python (Backend)
- **PEP 8** 스타일 가이드 준수
- **Type hints** 사용 권장
- **Docstring** 작성 (Google 스타일)
- **Black** 포매터 사용

```python
def analyze_employee_performance(
    employee_id: str, 
    text_data: str, 
    quantitative_data: Dict[str, float]
) -> PerformanceResult:
    """직원 성과를 분석합니다.
    
    Args:
        employee_id: 직원 고유 ID
        text_data: 정성적 평가 텍스트
        quantitative_data: 정량적 성과 데이터
        
    Returns:
        PerformanceResult: 분석 결과 객체
        
    Raises:
        ValueError: 잘못된 입력 데이터인 경우
    """
    pass
```

### JavaScript/TypeScript (Frontend)
- **ESLint** + **Prettier** 설정 준수
- **함수형 컴포넌트** 우선 사용
- **TypeScript** 타입 정의 필수

```typescript
interface EmployeeScore {
  employeeId: string;
  scores: {
    [dimension: string]: number;
  };
  overallScore: number;
  grade: string;
}

const EmployeeCard: React.FC<{ employee: EmployeeScore }> = ({ employee }) => {
  // 컴포넌트 구현
};
```

---

## 📋 **커밋 메시지 규칙**

### 형식
```
<type>(<scope>): <description>

<body>

<footer>
```

### 타입 (Type)
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 스타일 변경 (기능 변경 없음)
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 설정, 패키지 관리 등
- `perf`: 성능 개선
- `ci`: CI/CD 설정 변경

### 범위 (Scope)
- `api`: API 관련
- `ui`: UI 관련
- `db`: 데이터베이스 관련
- `auth`: 인증 관련
- `analysis`: 분석 엔진 관련

### 예시
```
feat(analysis): 8차원 성과 분석 알고리즘 추가

- 업무성과, 리더십협업 등 8개 차원 분석 로직 구현
- 가중치 기반 종합 점수 계산 기능
- OpenAI GPT 연동 피드백 생성

Closes #123
```

---

## 🧪 **테스트**

### 테스트 작성 필수
- 새로운 기능에는 반드시 테스트 코드 작성
- 기존 테스트가 모두 통과해야 함
- 테스트 커버리지 80% 이상 유지

### 테스트 실행
```bash
# 전체 테스트 실행
python comprehensive_test_v4.py

# 특정 모듈 테스트
python -m pytest tests/test_analysis.py -v

# 커버리지 측정
python -m pytest --cov=app tests/
```

---

## 📁 **프로젝트 구조**

```
airiss_v4/
├── app/                    # 백엔드 애플리케이션
│   ├── api/               # API 라우터
│   ├── core/              # 핵심 설정
│   ├── db/                # 데이터베이스
│   ├── models/            # 데이터 모델
│   ├── services/          # 비즈니스 로직
│   └── utils/             # 유틸리티
├── airiss-v4-frontend/    # 프론트엔드
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── services/      # API 서비스
│   │   └── utils/         # 유틸리티
├── tests/                 # 테스트 코드
├── scripts/               # 유틸리티 스크립트
└── docs/                  # 문서
```

---

## 🔍 **코드 리뷰 프로세스**

### Pull Request 체크리스트
- [ ] 이슈와 연결되어 있음
- [ ] 테스트 코드가 포함되어 있음
- [ ] 모든 테스트가 통과함
- [ ] 코드 스타일이 일관됨
- [ ] 문서가 업데이트됨 (필요한 경우)
- [ ] 성능에 미치는 영향을 고려함

### 리뷰어 가이드라인
- 코드의 가독성과 유지보수성 중점 검토
- 보안 취약점 확인
- 성능상 이슈 점검
- API 설계 일관성 검토

---

## 🛡️ **보안 가이드라인**

### 중요 원칙
- **개인정보는 절대 로그에 기록하지 않음**
- **하드코딩된 비밀키 금지**
- **SQL Injection 방지**
- **XSS 공격 방어**

### 보안 체크리스트
- [ ] 입력 데이터 검증
- [ ] 출력 데이터 이스케이프
- [ ] 인증/권한 확인
- [ ] 암호화 적용 (필요시)
- [ ] 보안 헤더 설정

---

## 📖 **문서 작성**

### API 문서
- **OpenAPI/Swagger** 스펙 업데이트
- **예제 코드** 포함
- **에러 케이스** 명시

### 코드 문서
- **함수/클래스 Docstring** 작성
- **복잡한 로직 주석** 추가
- **README.md** 업데이트 (필요시)

---

## 🎯 **개발 환경 설정**

### 1. 저장소 클론
```bash
git clone https://github.com/joonbary/airiss_enterprise.git
cd airiss_enterprise
```

### 2. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 프리커밋 훅 설정
```bash
pip install pre-commit
pre-commit install
```

### 4. IDE 설정
- **VSCode**: `.vscode/settings.json` 사용
- **PyCharm**: 프로젝트 설정 import

---

## 🤔 **도움이 필요한 경우**

### 문의 채널
- **GitHub Discussions**: 일반적인 질문
- **Slack**: #airiss-dev (내부 채널)
- **이메일**: airiss-dev@okfinancial.com

### 멘토링
- 신규 기여자를 위한 1:1 멘토링 제공
- 코드 리뷰 과정에서 상세한 피드백 제공

---

## 🏆 **기여자 인정**

### 기여 유형
- **코드 기여**: 새 기능, 버그 수정, 성능 개선
- **문서 기여**: 문서 작성, 번역, 개선
- **테스트 기여**: 테스트 코드 작성, 버그 리포트
- **리뷰 기여**: 코드 리뷰, 이슈 트리아지

### 인정 방법
- **README.md 기여자 섹션**에 이름 추가
- **릴리스 노트**에 기여 내용 명시
- **사내 표창** (OK금융그룹 임직원)

---

## 📊 **성과 지표**

우리는 다음 지표로 프로젝트 건강성을 측정합니다:

- **코드 품질**: SonarQube 점수 A등급 이상
- **테스트 커버리지**: 80% 이상
- **성능**: API 응답시간 < 500ms
- **보안**: 알려진 취약점 0개
- **문서화**: API 문서 완성도 100%

---

## 🎉 **기여자 행동 강령**

모든 기여자는 [Contributor Covenant](https://www.contributor-covenant.org/)를 준수해야 합니다.

핵심 원칙:
- **존중**: 다양한 의견과 경험을 존중
- **포용**: 모든 기여자를 환영
- **협력**: 건설적인 피드백과 토론
- **전문성**: 기술적 우수성 추구

---

**AIRISS와 함께 HR의 미래를 만들어갑시다!** 🚀

*이 문서는 프로젝트 발전에 따라 지속적으로 업데이트됩니다.*
