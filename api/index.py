from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. 简单的握手，避免直接访问报错
            if self.path == '/' or self.path == '/favicon.ico':
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Proxy is running!".encode('utf-8'))
                return

            # 2. 获取 ?url= 后面的参数
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            target_url = params.get('url', [None])[0]

            if not target_url:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write("<h1>服务正常！</h1><p>请在网址后面加上参数: ?url=https://www.google.com</p>".encode('utf-8'))
                return

            # 3. 发起请求 (逻辑直接写在这里，避免函数名冲突)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # 发送请求到目标网站
            req = urllib.request.Request(target_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                self.send_response(response.status)
                
                # 转发 Content-Type
                if response.getheader('Content-Type'):
                    self.send_header('Content-type', response.getheader('Content-Type'))
                
                # 允许跨域
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # 返回内容
                self.wfile.write(response.read())

        except Exception:
            # 4. 错误处理：把错误打印在网页上
            error_msg = traceback.format_exc()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"Server Error Log:\n{error_msg}".encode('utf-8'))
