import os
import http.server
import socketserver

# 强制切换到正确的目录
dashboard_dir = r"D:\dev\found\family-wealth\software-modules\sandbox-system\dashboard"
os.chdir(dashboard_dir)

# 确认当前目录
print("当前工作目录:", os.getcwd())
print("目录内容:")
for item in os.listdir('.'):
    if item.endswith('.html'):
        print(f"  HTML文件: {item}")

# 启动服务器
PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"服务器启动在端口 {PORT}")
    print(f"访问地址: http://localhost:{PORT}")
    httpd.serve_forever()