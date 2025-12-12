"""
Simple web server for serving the frontend.
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support."""
    
    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.end_headers()


def run_server(port=8080):
    """
    Run the web server.
    
    Args:
        port: Port number to run the server on
    """
    # Change to frontend directory
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    os.chdir(frontend_dir)
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    
    print(f'Starting web server on http://localhost:{port}')
    print('Press Ctrl+C to stop')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        httpd.shutdown()


if __name__ == '__main__':
    run_server(8080)

