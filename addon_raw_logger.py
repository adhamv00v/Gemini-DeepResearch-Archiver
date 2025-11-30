import os
import time
from mitmproxy import http

# このファイルが置かれているディレクトリ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ログ保存先ディレクトリ
LOG_DIR = os.path.join(BASE_DIR, "captured_data")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


class GeminiRawLogger:
    """
    Gemini 関連の HTTP レスポンスを
    「生のテキスト」のまま保存するだけのシンプルなロガー
    """

    # 監視対象の URL の一部
    TARGET_KEYWORDS = [
        "batchexecute",          # Deep Research を含むことが多い
        "streamGenerateContent", # ストリーム生成系
        "gemini.google.com",     # 念のためドメインでもフィルタ
    ]

    def response(self, flow: http.HTTPFlow) -> None:
        """
        サーバからレスポンスを受け取ったときに毎回呼ばれる
        """
        url = flow.request.pretty_url

        # 監視対象でなければ何もしない
        if not any(key in url for key in self.TARGET_KEYWORDS):
            return

        try:
            # レスポンスボディをテキストとして取得
            # strict=False にすると、デコードに失敗しても
            # 可能な範囲で文字列化してくれる
            text = flow.response.get_text(strict=False)

            if not text:
                # 何もなければログしない
                return

            # ファイル名用タイムスタンプ
            # 例: 2025-11-30_15-23-45_123456
            ts = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(flow.request.timestamp_start))
            ms = int((flow.request.timestamp_start - int(flow.request.timestamp_start)) * 1000)
            safe_ts = f"{ts}_{ms:03d}"

            # URL からざっくり種別を付ける
            if "batchexecute" in url:
                kind = "batchexecute"
            elif "streamGenerateContent" in url:
                kind = "stream"
            else:
                kind = "other"

            filename = os.path.join(LOG_DIR, f"{safe_ts}_{kind}.txt")

            # ログファイルに書き出し
            with open(filename, "w", encoding="utf-8", errors="replace") as f:
                # メタ情報も少しだけヘッダとして付けておくと後で便利
                f.write(f"### URL\n{url}\n\n")
                f.write("### RESPONSE BODY (raw)\n")
                f.write(text)

            print(f"[GeminiRawLogger] Saved: {filename}")

        except Exception as e:
            # 例外が出ても mitmproxy 本体は落とさない
            print(f"[GeminiRawLogger] Error while saving response: {e}")


# mitmproxy にこのアドオンを登録
addons = [
    GeminiRawLogger()
]
