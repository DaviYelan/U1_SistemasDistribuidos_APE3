import http.server
import socketserver

PORT = 3000

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Frontend corriendo en http://localhost:{PORT}")
    httpd.serve_forever()