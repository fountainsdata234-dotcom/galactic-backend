from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import ssl
import certifi

# Nuclear SSL Fix for Vercel
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

app = Flask(__name__)
# Allow CORS for Netlify
CORS(app, resources={r"/*": {"origins": "*"}})

# --- 1. THE HOME ROUTE (Fixes the "Not Found" on the main link) ---
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Alive",
        "message": "Galactic Backend is running successfully.",
        "usage": "Send requests to /api/get-video?url=YOUR_VIDEO_URL"
    })

# --- 2. THE DOWNLOAD ROUTE ---
@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'simulate': True, 
            'skip_download': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get('url', None)
            
            if not download_url and 'entries' in info:
                try: download_url = info['entries'][0].get('url')
                except: pass

            if not download_url:
                 return jsonify({'status': 'error', 'message': 'Could not extract link.'}), 500

            response = jsonify({
                'status': 'success',
                'title': info.get('title', 'Galactic Video'),
                'thumbnail': info.get('thumbnail', ''),
                'download_url': download_url
            })
            return response

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- 3. CONTACT ROUTE ---
@app.route('/api/contact', methods=['POST'])
def contact():
    return jsonify({'status': 'success', 'message': 'Message received'})
