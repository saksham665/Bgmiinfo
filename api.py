from http.server import BaseHTTPRequestHandler
import json
import requests
import urllib.parse

def handler(request, response):
    try:
        # Parse query parameters
        query_params = request.get('query', {})
        path = request.get('path', '')
        
        # Only handle /fetch route
        if path != '/fetch':
            response.status(404).send('')
            return
        
        # Get UID from query parameter
        uid = query_params.get('uid', [None])[0] if isinstance(query_params.get('uid'), list) else query_params.get('uid')
        
        if not uid:
            response_data = {
                "success": False,
                "error": "Missing uid parameter"
            }
            response.status(400).json(response_data)
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
        
        api_response = requests.post(
            url, 
            headers=headers, 
            json=data,
            timeout=10
        )
        
        # Process the response
        if api_response.status_code == 200:
            original_data = api_response.json()
            
            # Convert Unicode escape sequences to normal text
            if 'username' in original_data:
                try:
                    original_data['username'] = original_data['username'].encode('latin-1').decode('unicode_escape')
                except:
                    pass
            
            response.status(200).json(original_data)
            
        else:
            error_response = {
                "success": False,
                "error": f"External API returned status code: {api_response.status_code}"
            }
            response.status(502).json(error_response)
            
    except requests.exceptions.Timeout:
        error_response = {
            "success": False,
            "error": "Request timeout"
        }
        response.status(504).json(error_response)
        
    except requests.exceptions.RequestException as e:
        error_response = {
            "success": False,
            "error": "Network error"
        }
        response.status(502).json(error_response)
        
    except json.JSONDecodeError:
        error_response = {
            "success": False,
            "error": "Invalid JSON response from external API"
        }
        response.status(502).json(error_response)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": "Internal server error"
        }
        response.status(500).json(error_response)
