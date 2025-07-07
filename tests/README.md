# AIRISS Backend Tests

이 디렉토리는 AIRISS 백엔드의 단위 테스트를 포함합니다.

## 테스트 구조

```
tests/
├── unit/           # 단위 테스트
├── integration/    # 통합 테스트  
└── e2e/           # 엔드투엔드 테스트
```

## 실행 방법

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app

# 특정 테스트 파일 실행
pytest tests/unit/test_api.py
```
