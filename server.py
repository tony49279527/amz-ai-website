import http.server
import socketserver
import json
import sys
import os

# Load .env manually since python-dotenv might not be available
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Import our backend logic
sys.path.append('.')
from api.analysis import process_analysis_request

PORT = int(os.environ.get('PORT', 8000))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # 1. Routing: Only handle /api/analysis
        if self.path == '/api/analysis':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Call our Serverless Function logic
                response_data, status_code = process_analysis_request(data)
                
                self.send_response(status_code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
        else:
            self.send_error(404, "Not Found")

print(f"Server started at http://localhost:{PORT}")
print(f"Backend API available at http://localhost:{PORT}/api/analysis")

# Allow address reuse to prevent "Address already in use" errors during quick restarts
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    httpd.serve_forever()
