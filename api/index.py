from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Allow requests from your website
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "XTRACTION V4 Neural Core Online"})

# --- 1. TIKTOK SPECIALIST ---
def handle_tiktok(url):
    try:
        api_url = "https://www.tikwm.com/api/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}
        data = { "url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1 }
        
        response = requests.post(api_url, data=data, headers=headers, timeout=10)
        json_data = response.json()
        
        if json_data.get('code') == 0:
            d = json_data.get('data', {})
            # Prefer HD, fallback to standard
            final_url = d.get('hdplay') or d.get('play') or d.get('wmplay')
            # Get High Res Cover
            cover = d.get('origin_cover') or d.get('cover')
            
            if final_url and not final_url.startswith('http'):
                final_url = "https://www.tikwm.com" + final_url
                
            return {
                'status': 'success',
                'title': d.get('title', 'XTRACTION TikTok Media'),
                'thumbnail': cover,
                'download_url': final_url,
                'platform': 'TikTok'
            }
        return None
    except: return None

# --- 2. UNIVERSAL SPECIALIST (Cobalt) ---
def handle_cobalt(url):
    # Server Swarm (The Hydra)
    instances = [
        "https://api.cobalt.tools/api/json",
        "https://cobalt.xyzen.tech/api/json",
        "https://api.wuk.sh/api/json"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"
    }
    
    # Force H264 (MP4) to prevent "Audio Only" issues on YouTube
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
                
                link = None
                if data.get('status') == 'stream': link = data.get('url')
                elif data.get('status') == 'picker': link = data.get('picker')[0].get('url')
                elif data.get('status') == 'redirect': link = data.get('url')
                
                if link:
                    return {
                        'status': 'success',
                        'title': data.get('filename', 'XTRACTION Universal Media'),
                        'thumbnail': 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png', # Placeholder for non-TikTok
                        'download_url': link,
                        'platform': 'Universal'
                    }
        except: continue
    return None

@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url: return jsonify({'status': 'error', 'message': 'Input empty.'}), 400

    result = None
    if "tiktok.com" in url: result = handle_tiktok(url)
    if not result: result = handle_cobalt(url)

    if result: return jsonify(result)
    else: return jsonify({'status': 'error', 'message': 'Could not extract media. Link might be private.'}), 500
