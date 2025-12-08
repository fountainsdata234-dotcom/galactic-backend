from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# Allow requests from your Netlify Frontend
CORS(app, resources={r"/*": {"origins": "*"}})

# --- FREE PUBLIC API (COBALT) ---
# This is a robust, free instance.
# If this one ever goes down, you can find other "Cobalt Instances" on Google.
COBALT_API_URL = "https://api.cobalt.tools/api/json"

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Alive", "message": "Galactic Backend (Cobalt Bridge) is running."})

@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    try:
        # Prepare the request to Cobalt
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "GalacticSearch-Client/1.0"
        }
        
        payload = {
            "url": url,
            "vCodec": "h264", # Ensures compatibility
            "vQuality": "720",
            "isAudioOnly": False,
            "isNoTTWatermark": True # Remove Tiktok Watermark
        }

        # Send request to the Free API
        response = requests.post(COBALT_API_URL, json=payload, headers=headers)
        
        # Check if the API is happy
        if response.status_code != 200:
             return jsonify({'status': 'error', 'message': 'The Galactic sensors could not lock onto the video. Try again.'}), 500

        data = response.json()

        # Cobalt returns different structures based on the result
        # Scenario A: Direct Stream (Success)
        if data.get('status') == 'stream':
            return jsonify({
                'status': 'success',
                'title': data.get('filename', 'Galactic Video'),
                # Cobalt doesn't always send a thumb, so we use a cool placeholder or the favicon
                'thumbnail': "https://cdn-icons-png.flaticon.com/512/3135/3135715.png", 
                'download_url': data.get('url')
            })
            
        # Scenario B: Picker (Multiple qualities found)
        elif data.get('status') == 'picker':
            # We just grab the first available video
            first_item = data.get('picker')[0]
            return jsonify({
                'status': 'success',
                'title': "Galactic Video (Multiple Formats)",
                'thumbnail': "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                'download_url': first_item.get('url')
            })

        # Scenario C: Error
        else:
            return jsonify({'status': 'error', 'message': 'Transmission Interrupted.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    return jsonify({'status': 'success', 'message': 'Message received'})
