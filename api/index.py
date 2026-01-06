from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def handle_request(self, method):
        try:
            # 1. 获取目标 URL (从查询参数 ?url=... 获取)
            path_parts = self.path.split('?url=')
            if len(path_parts) < 2:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Error: Missing url parameter. Usage: ?url=https://example.com")
                return
            
            target_url = path_parts[1]
            
            # 2. 如果是 POST，读取请求体
            data = None
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    data = self.rfile.read(content_length)

            # 3. 伪装 User-Agent 防止被秒封
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*'
            }
            
            # 如果客户端传了 Content-Type，透传过去
            if self.headers.get('Content-Type'):
                headers['Content-Type'] = self.headers.get('Content-Type')

            # 4. 发起请求
            req = urllib.request.Request(target_url, data=data, headers=headers, method=method)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                # 5. 返回结果
                self.send_response(response.status)
                
                # 透传响应头 (除了 hop-by-hop headers)
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-encoding', 'connection']:
                        self.send_header(key, value)
                
                # 允许跨域
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(str(e.reason).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
