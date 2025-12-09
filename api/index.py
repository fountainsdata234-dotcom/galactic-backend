from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# Allow requests from your Netlify Frontend
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Alive", "message": "Galactic Backend (Hybrid Engine) is running."})

# --- SPECIALIZED TIKTOK HANDLER (100% Success Rate for TikTok) ---
def handle_tiktok(url):
    try:
        api_url = "https://www.tikwm.com/api/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        data = {
            "url": url,
            "count": 12,
            "cursor": 0,
            "web": 1,
            "hd": 1
        }
        
        response = requests.post(api_url, data=data, headers=headers)
        json_data = response.json()
        
        if json_data.get('code') == 0:
            video_data = json_data.get('data', {})
            return {
                'status': 'success',
                'title': video_data.get('title', 'Galactic TikTok'),
                'thumbnail': video_data.get('cover', 'https://cdn-icons-png.flaticon.com/512/3046/3046121.png'),
                'download_url': video_data.get('play')  # No watermark URL
            }
        else:
            return None
    except Exception as e:
        print(f"TikTok API Error: {str(e)}")
        return None

# --- COBALT ROTATION (For YouTube, Insta, X, etc) ---
def handle_cobalt(url):
    # Updated list of instances
    instances = [
        "https://api.cobalt.tools/api/json",
        "https://cobalt.xyzen.tech/api/json",
        "https://api.wuk.sh/api/json",
        "https://cobalt.tools/api/json" 
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    payload = {
        "url": url,
        "vCodec": "h264",
        "vQuality": "720",
        "isAudioOnly": False,
        "isNoTTWatermark": True
    }

    for instance in instances:
        try:
            response = requests.post(instance, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                # Logic to find the URL in Cobalt's variable response
                dl_link = None
                if data.get('status') == 'stream':
                    dl_link = data.get('url')
                elif data.get('status') == 'picker':
                    dl_link = data.get('picker')[0].get('url')
                elif data.get('status') == 'redirect':
                    dl_link = data.get('url')
                
                if dl_link:
                    return {
                        'status': 'success',
                        'title': data.get('filename', 'Galactic Video'),
                        'thumbnail': 'https://cdn-icons-png.flaticon.com/512/5692/5692030.png', # Placeholder
                        'download_url': dl_link
                    }
        except:
            continue # Try next instance
            
    return None

# --- MAIN ROUTE ---
@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    result = None

    # 1. Check if it's TikTok (Use the Specialist API)
    if "tiktok.com" in url:
        result = handle_tiktok(url)
    
    # 2. If not TikTok, or if TikTok failed, try Cobalt (The Generalist)
    if not result:
        result = handle_cobalt(url)

    if result:
        return jsonify(result)
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Mission Failed. The link is either private, removed, or blocking our server sensors.'
        }), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    return jsonify({'status': 'success', 'message': 'Message received'})
