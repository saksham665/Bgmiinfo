from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            from urllib.parse import urlparse, parse_qs
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            # Get UID from query parameter
            uid = query_params.get('uid', [None])[0]
            
            if not uid:
                response_data = {
                    "success": False,
                    "error": "Missing uid parameter"
                }
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
                return
            
            # Make request to darkuc API
            url = "https://darkuc.net/bin.php"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
                'Content-Type': 'application/json',
            }
            data = {"char_id": str(uid)}
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                original_data = response.json()
                
                # Convert Unicode escape sequences
                if 'username' in original_data:
                    try:
                        original_data['username'] = original_data['username'].encode('latin-1').decode('unicode_escape')
                    except:
                        pass
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(original_data, ensure_ascii=False).encode('utf-8'))
            else:
                error_response = {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
                self.send_response(502)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode())
                
        except Exception as e:
            error_response = {
                "success": False,
                "error": "Server error"
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
