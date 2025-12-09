from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- SERVER ROTATION LIST ---
# We try these one by one. If one blocks us, we move to the next.
COBALT_INSTANCES = [
    "https://api.cobalt.tools/api/json",       # Official (Often busy)
    "https://cobalt.xyzen.tech/api/json",      # Mirror 1
    "https://api.wuk.sh/api/json",             # Mirror 2
    "https://cobalt.tools/api/json"            # Alternate
]

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Alive", "message": "Galactic Backend (Multi-Server Bridge) is running."})

@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    # HEADERS: We must look like a real browser, not a script
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://cobalt.tools",
        "Referer": "https://cobalt.tools/"
    }

    payload = {
        "url": url,
        "vCodec": "h264",
        "vQuality": "720",
        "isAudioOnly": False,
        "isNoTTWatermark": True
    }

    # --- THE HYDRA LOOP ---
    last_error = ""
    
    for api_server in COBALT_INSTANCES:
        try:
            # print(f"Trying server: {api_server}") # For logs
            response = requests.post(api_server, json=payload, headers=headers, timeout=10)
            
            # If we get a valid success code (200), we stop looking
            if response.status_code == 200:
                data = response.json()
                
                # Success Type A: Direct Stream
                if data.get('status') == 'stream':
                    return jsonify({
                        'status': 'success',
                        'title': data.get('filename', 'Galactic Video'),
                        'thumbnail': "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                        'download_url': data.get('url')
                    })
                
                # Success Type B: Picker (Multiple options)
                elif data.get('status') == 'picker':
                    first_item = data.get('picker')[0]
                    return jsonify({
                        'status': 'success',
                        'title': "Galactic Video (Best Quality)",
                        'thumbnail': "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                        'download_url': first_item.get('url')
                    })
                
                # Success Type C: Redirect (Sometimes happens)
                elif data.get('status') == 'redirect':
                     return jsonify({
                        'status': 'success',
                        'title': "Galactic Video",
                        'thumbnail': "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                        'download_url': data.get('url')
                    })

            # If status wasn't 200, save error and loop to next server
            last_error = f"Server {api_server} returned {response.status_code}"
            
        except Exception as e:
            last_error = str(e)
            continue # Try next server immediately

    # If we finish the loop and nothing worked:
    return jsonify({
        'status': 'error', 
        'message': 'All Galactic sensors failed. The video might be private or region-locked.',
        'debug': last_error
    }), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    return jsonify({'status': 'success', 'message': 'Message received'})
