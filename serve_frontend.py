#!/usr/bin/env python3
"""
Simple HTTP server for the Language Teacher frontend
Serves the frontend.html file to avoid CORS issues with file:// URLs
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_frontend():
    """Serve the frontend HTML file"""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    frontend_file = script_dir / "frontend.html"
    
    if not frontend_file.exists():
        print(f"Error: frontend.html not found at {frontend_file}")
        return
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Create a custom handler that serves the HTML file
    class FrontendHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.path = '/frontend.html'
            return super().do_GET()
    
    # Start the server
    PORT = 3000
    
    with socketserver.TCPServer(("", PORT), FrontendHandler) as httpd:
        print(f"Frontend server running at http://localhost:{PORT}")
        print("Opening browser...")
        
        # Open the browser
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down frontend server...")
            httpd.shutdown()

if __name__ == "__main__":
    serve_frontend()
