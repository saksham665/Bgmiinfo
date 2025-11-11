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
        'origin': 'https://darkuc.net',
        'referer': 'https://darkuc.net/',
    }

    data = {"char_id": str(uid)}

    # Shorter timeout to avoid Vercel function crash
    response = requests.post(url, headers=headers, json=data, timeout=5)
    return response


@app.route('/fetch', methods=['GET'])
def fetch_data():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"success": False, "error": "Missing uid parameter"}), 400

    try:
        response = fetch_character_data(uid)

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"External API returned {response.status_code}"
            }), 502

        try:
            original_data = response.json()
        except:
            return jsonify({"success": False, "error": "Invalid JSON response"}), 502

        # Decode unicode escape sequences in username (if any)
        if 'username' in original_data:
            try:
                original_data['username'] = original_data['username'].encode('latin-1').decode('unicode_escape')
            except Exception:
                pass

        return app.response_class(
            response=json.dumps(original_data, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )

    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "Request timeout"}), 504

    except requests.exceptions.RequestException:
        return jsonify({"success": False, "error": "Network error"}), 502

    except Exception as e:
        return jsonify({"success": False, "error": "Internal server error"}), 500


@app.route('/')
def home():
    return jsonify({
        "message": "BGMI UID API is running",
        "usage": "/fetch?uid=<your_uid>"
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
