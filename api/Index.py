from http.server import BaseHTTPRequestHandler
import json
import requests
import urllib.parse
import sys
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # Only handle /fetch route
            if parsed_path.path != '/fetch':
                self.send_response(404)
                self.end_headers()
                return
            
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
            
            # Make request to the original API
            url = "https://darkuc.net/bin.php"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Content-Type': 'application/json',
                'sec-ch-ua-platform': '"Android"',
                'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
                'sec-ch-ua-mobile': '?1',
                'origin': 'https://darkuc.net',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://darkuc.net/',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'priority': 'u=1, i'
            }
            
            data = {
                "char_id": str(uid)
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=data,
                timeout=10
            )
            
            # Process the response
            if response.status_code == 200:
                original_data = response.json()
                
                # Convert Unicode escape sequences to normal text
                if 'username' in original_data:
                    try:
                        original_data['username'] = original_data['username'].encode('latin-1').decode('unicode_escape')
                    except:
                        pass
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(original_data, ensure_ascii=False).encode('utf-8'))
                
            else:
                error_response = {
                    "success": False,
                    "error": f"External API returned status code: {response.status_code}"
                }
                self.send_response(502)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode())
                
        except requests.exceptions.Timeout:
            error_response = {
                "success": False,
                "error": "Request timeout"
            }
            self.send_response(504)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
            
        except requests.exceptions.RequestException as e:
            error_response = {
                "success": False,
                "error": "Network error"
            }
            self.send_response(502)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
            
        except json.JSONDecodeError:
            error_response = {
                "success": False,
                "error": "Invalid JSON response from external API"
            }
            self.send_response(502)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": "Internal server error"
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        # Handle POST requests if needed
        self.do_GET()
