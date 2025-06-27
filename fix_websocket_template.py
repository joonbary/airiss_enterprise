"""
AIRISS v4.1 WebSocket 템플릿 변수 수정 스크립트
main.py의 템플릿 변수 문제를 해결합니다.
"""

import os
import re

def fix_main_py():
    """main.py 파일의 WebSocket 연결 코드를 수정"""
    
    print("🔧 main.py 파일 수정 시작...")
    
    # main.py 파일 읽기
    main_py_path = os.path.join(os.path.dirname(__file__), "app", "main.py")
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 백업 생성
    backup_path = main_py_path + '.backup_websocket'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 백업 파일 생성: {backup_path}")
    
    # WebSocket 연결 코드 수정
    # 패턴 1: {{ ws_host }}:{{ server_port }} 형태를 찾아서 수정
    old_pattern = r'ws://\{\{ ws_host \}\}:\{\{ server_port \}\}'
    new_code = 'ws://${window.location.hostname || "localhost"}:${window.location.port || "8002"}'
    
    # 패턴 2: {WS_HOST}:{SERVER_PORT} 형태도 확인
    old_pattern2 = r'ws://\{WS_HOST\}:\{SERVER_PORT\}'
    
    # 수정 수행
    modified = False
    
    # 첫 번째 패턴 찾기 및 수정
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_code, content)
        modified = True
        print("✅ {{ ws_host }}:{{ server_port }} 패턴 수정됨")
    
    # 두 번째 패턴 찾기 및 수정
    if re.search(old_pattern2, content):
        content = re.sub(old_pattern2, new_code, content)
        modified = True
        print("✅ {WS_HOST}:{SERVER_PORT} 패턴 수정됨")
    
    # JavaScript 템플릿 리터럴 내부의 WebSocket URL 수정
    # connectWebSocket 함수 내부의 ws = new WebSocket 부분 찾기
    ws_pattern = r'(ws\s*=\s*new\s+WebSocket\s*\(\s*`ws://)(.*?)(/ws/\$\{clientId\})'
    
    def replace_ws_url(match):
        return match.group(1) + '${window.location.hostname || "localhost"}:${window.location.port || "8002"}' + match.group(3)
    
    if re.search(ws_pattern, content):
        content = re.sub(ws_pattern, replace_ws_url, content)
        modified = True
        print("✅ WebSocket URL 동적 할당으로 수정됨")
    
    if modified:
        # 수정된 내용 저장
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ main.py 파일이 성공적으로 수정되었습니다!")
        return True
    else:
        print("⚠️ 수정할 패턴을 찾지 못했습니다.")
        # get_main_html 함수 내부를 더 자세히 확인
        if 'function connectWebSocket()' in content:
            print("📌 connectWebSocket 함수는 존재합니다.")
            # 함수 주변 코드 출력
            ws_func_start = content.find('function connectWebSocket()')
            if ws_func_start != -1:
                ws_func_snippet = content[ws_func_start:ws_func_start+500]
                print("📝 현재 코드:")
                print("-" * 50)
                print(ws_func_snippet)
                print("-" * 50)
        
        return False

def fix_dashboard_html():
    """dashboard.html은 이미 수정되었는지 확인"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "app", "templates", "dashboard.html")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'window.location.hostname' in content:
        print("✅ dashboard.html은 이미 수정되어 있습니다.")
        return True
    else:
        print("⚠️ dashboard.html도 수정이 필요할 수 있습니다.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AIRISS v4.1 WebSocket 템플릿 변수 수정 스크립트")
    print("=" * 60)
    print()
    
    # main.py 수정
    main_fixed = fix_main_py()
    print()
    
    # dashboard.html 확인
    dashboard_fixed = fix_dashboard_html()
    print()
    
    if main_fixed:
        print("🎉 수정이 완료되었습니다!")
        print("🚀 서버를 재시작하여 변경사항을 적용하세요.")
    else:
        print("❓ 자동 수정에 실패했습니다.")
        print("💡 수동으로 다음 사항을 확인하세요:")
        print("   1. main.py의 connectWebSocket 함수에서 WebSocket URL 부분")
        print("   2. ws://{{ ws_host }}:{{ server_port }} 형태의 템플릿 변수")
        print("   3. 동적으로 호스트와 포트를 가져오도록 수정:")
        print("      ws://${window.location.hostname || 'localhost'}:${window.location.port || '8002'}")
