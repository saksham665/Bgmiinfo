from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

def fetch_character_data(uid):
    """Fetch character data from darkuc.net API"""
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
    
    data = {"char_id": str(uid)}
    
    response = requests.post(url, headers=headers, json=data, timeout=10)
    return response

@app.route('/fetch', methods=['GET'])
def fetch_data():
    try:
        # Get UID from query parameter
        uid = request.args.get('uid')
        
        if not uid:
            return jsonify({
                "success": False,
                "error": "Missing uid parameter"
            }), 400
        
        # Make request to the original API
        response = fetch_character_data(uid)
        
        if response.status_code == 200:
            original_data = response.json()
            
            # Convert Unicode escape sequences to normal text
            if 'username' in original_data:
                try:
                    # Handle unicode escape sequences
                    original_data['username'] = original_data['username'].encode('latin-1').decode('unicode_escape')
                except:
                    # If decoding fails, keep original
                    pass
            
            # Return raw JSON response without Source_Developer
            return app.response_class(
                response=json.dumps(original_data, ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        else:
            return jsonify({
                "success": False,
                "error": f"External API returned status code: {response.status_code}"
            }), 502
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Request timeout"
        }), 504
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "error": "Network error"
        }), 502
        
    except json.JSONDecodeError:
        return jsonify({
            "success": False,
            "error": "Invalid JSON response from external API"
        }), 502
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/')
def home():
    # Return empty response with 404 status
    return '', 404

# Handle all other routes with 404
@app.errorhandler(404)
def not_found(e):
    return '', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)