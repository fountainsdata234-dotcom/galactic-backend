from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# Allow requests from your Netlify Frontend
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Alive", "message": "Galactic Backend is running."})

# --- SPECIALIZED TIKTOK HANDLER ---
def handle_tiktok(url):
    try:
        api_url = "https://www.tikwm.com/api/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        data = { "url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1 }
        
        response = requests.post(api_url, data=data, headers=headers)
        json_data = response.json()
        
        if json_data.get('code') == 0:
            video_data = json_data.get('data', {})
            
            # IMPROVED EXTRACTION: Try HD first, then Play, then WM
            # We explicitly prefer the 'hdplay' or 'play' link
            final_url = video_data.get('hdplay') or video_data.get('play') or video_data.get('wmplay')
            
            # Use default galaxy icon if cover is missing/broken
            cover = video_data.get('cover')
            if not cover: 
                cover = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

            if final_url:
                # IMPORTANT: Ensure URL is absolute (TikWM sometimes sends relative paths)
                if not final_url.startswith('http'):
                    final_url = "https://www.tikwm.com" + final_url

                return {
                    'status': 'success',
                    'title': video_data.get('title', 'Galactic TikTok'),
                    'thumbnail': cover,
                    'download_url': final_url
                }
        return None
    except Exception as e:
        print(f"TikTok API Error: {str(e)}")
        return None

# --- COBALT ROTATION (Others) ---
def handle_cobalt(url):
    instances = [
        "https://api.cobalt.tools/api/json",
        "https://cobalt.xyzen.tech/api/json",
        "https://api.wuk.sh/api/json"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    payload = {
        "url": url, "vCodec": "h264", "vQuality": "720", "isAudioOnly": False, "isNoTTWatermark": True
    }

    for instance in instances:
        try:
            response = requests.post(instance, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                dl_link = None
                if data.get('status') == 'stream': dl_link = data.get('url')
                elif data.get('status') == 'picker': dl_link = data.get('picker')[0].get('url')
                elif data.get('status') == 'redirect': dl_link = data.get('url')
                
                if dl_link:
                    return {
                        'status': 'success',
                        'title': data.get('filename', 'Galactic Video'),
                        'thumbnail': 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png',
                        'download_url': dl_link
                    }
        except: continue
    return None

@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url: return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    result = None
    if "tiktok.com" in url: result = handle_tiktok(url)
    if not result: result = handle_cobalt(url)

    if result: return jsonify(result)
    else: return jsonify({'status': 'error', 'message': 'Could not extract video.'}), 500

@app.route('/api/contact', methods=['POST'])
def contact(): return jsonify({'status': 'success'})
