# test_imports.py
print("🔍 패키지 import 테스트 시작...\n")

try:
    import fastapi
    print(f"✅ FastAPI: {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI: {e}")

try:
    import pydantic
    print(f"✅ Pydantic: {pydantic.__version__}")
except ImportError as e:
    print(f"❌ Pydantic: {e}")

try:
    from pydantic_settings import BaseSettings
    print(f"✅ Pydantic Settings: OK")
except ImportError as e:
    print(f"❌ Pydantic Settings: {e}")

try:
    import pandas
    print(f"✅ Pandas: {pandas.__version__}")
except ImportError as e:
    print(f"❌ Pandas: {e}")

try:
    import websockets
    print(f"✅ WebSockets: {websockets.__version__}")
except ImportError as e:
    print(f"❌ WebSockets: {e}")

print("\n✅ 테스트 완료!")