import json
import os
import webbrowser
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

class WebServer:
    def __init__(self):
        self.app = Flask(__name__)
        
        # Enable CORS for development (when frontend runs on different port)
        CORS(self.app)
        
        # Configure static folder for Vite build (build directory)
        self.frontend_build_path = Path(__file__).parent.parent / "frontend" / "static"
        print(f"🔍 Frontend static path: {self.frontend_build_path}")
        print(f"🔍 Build path exists: {self.frontend_build_path.exists()}")
        if self.frontend_build_path.exists():
            print(f"🔍 Build contents: {list(self.frontend_build_path.iterdir())}")
        else:
            print("⚠️  Frontend static directory not found. Please run 'make build' in the frontend directory first.")
        
        # Don't set static_folder - we'll handle static files manually
        self.app.static_folder = None
        
        self.setup_routes()
        
    def setup_routes(self):
        # API Routes
        @self.app.route('/api/results')
        def get_all_results():
            """Get list of all evaluation results"""
            results_dir = Path("results")
            if not results_dir.exists():
                return jsonify({"results": []})
                
            results = []
            for json_file in results_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        results.append({
                            "filename": json_file.name,
                            "path": str(json_file),
                            "summary": data.get("summary", {}),
                            "created_at": self._extract_creation_time(data),
                            "file_size": json_file.stat().st_size
                        })
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
                    
            # Sort by creation time (newest first)
            results.sort(key=lambda x: x["created_at"], reverse=True)
            return jsonify({"results": results})
            
        @self.app.route('/api/results/<filename>')
        def get_specific_result(filename):
            """Get specific evaluation result by filename"""
            results_dir = Path("results")
            json_file = results_dir / filename
            
            if not json_file.exists():
                return jsonify({"error": "Result file not found"}), 404
                
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                return jsonify(data)
            except Exception as e:
                return jsonify({"error": f"Error reading file: {str(e)}"}), 500
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({"status": "healthy", "service": "rawbench-server"})
        
        # Static assets route for Vite build
        @self.app.route('/assets/<path:filename>')
        def serve_assets(filename):
            """Serve static assets from Vite build"""
            assets_dir = str(self.frontend_build_path / 'assets')
            try:
                return send_from_directory(assets_dir, filename)
            except Exception as e:
                print(f"Error serving asset {filename} from {assets_dir}: {e}")
                return f"Asset not found: {filename}", 404
        
        # Public assets route for files that should be accessible from root
        @self.app.route('/static_assets/<path:filename>')
        def serve_static_assets(filename):
            """Serve public assets from Vite build root"""
            try:
                return send_from_directory(self.frontend_build_path, filename)
            except Exception as e:
                print(f"Error serving static asset {filename}: {e}")
                return f"Asset not found: {filename}", 404
        
        # Favicon route
        @self.app.route('/favicon.ico')
        def serve_favicon():
            """Serve favicon"""
            try:
                return send_from_directory(self.frontend_build_path, 'favicon.ico')
            except:
                return "Favicon not found", 404
        
        # React Routes - Serve React app for all other routes (catch-all)
        @self.app.route('/')
        @self.app.route('/<path:path>')
        def serve_react(path=''):
            """Serve React app - handles client-side routing"""
            # Check if the path exists as a static file in the build directory
            if path and os.path.exists(os.path.join(self.frontend_build_path, path)):
                return send_from_directory(self.frontend_build_path, path)
            
            # For client-side routing, always serve index.html
            return send_from_directory(self.frontend_build_path, 'index.html')
    
    def _extract_creation_time(self, data: Dict[str, Any]) -> str:
        """Extract creation time from result data"""
        if "results" in data and data["results"]:
            # Get the first result's creation time
            first_result = data["results"][0]
            return first_result.get("created_at", "")
        return ""
    
    def serve_all_results(self, port: int = 8000):
        """Serve all results in the results directory"""
        self._start_server(port)
        
    def serve_specific_result(self, result_path: str, port: int = 8000):
        """Serve a specific result file"""
        # The result_path should be like "results/results_20250701_192446"
        # We need to find the actual JSON file
        results_dir = Path("results")
        json_file = results_dir / f"{Path(result_path).name}.json"
        
        if not json_file.exists():
            print(f"❌ Result file not found: {json_file}")
            return
        server_route = f"{Path(result_path).name}"
        self._start_server(port, specific_file=server_route)
    
    def _start_server(self, port: int = 8000, specific_file: Optional[str] = None):
        """Start the Flask server"""
        def open_browser():
            time.sleep(1)  # Give server time to start
            if specific_file:
                webbrowser.open(f"http://localhost:{port}/evaluation/{specific_file}")
            else:
                webbrowser.open(f"http://localhost:{port}")
        
        # Start browser in a separate thread
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"🌐 Starting RawBench server on http://localhost:{port}")
        print(f"📊 API endpoints available at http://localhost:{port}/api/")
        print(f"📱 Frontend served from: {self.frontend_build_path}")
        if not self.frontend_build_path.exists():
            print("⚠️  To build the frontend, run: cd frontend && make build")
        
        # Start Flask server
        self.app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    server = WebServer()
    server.serve_all_results(port=8000)
