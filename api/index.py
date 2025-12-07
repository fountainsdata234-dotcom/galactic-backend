from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import ssl
import certifi

# Nuclear SSL Fix
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Alive", "usage": "/api/get-video?url=..."})

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
            
            # --- FIX FOR NONETYPE ERROR ---
            if info is None:
                return jsonify({'status': 'error', 'message': 'The video platform blocked the request or the video is private.'}), 500
            
            # Smart URL extraction
            download_url = info.get('url', None)
            
            # If standard url failed, check entries (common for playlists/TikTok)
            if not download_url and 'entries' in info:
                entries = info.get('entries', [])
                if entries and entries[0]:
                    download_url = entries[0].get('url')

            if not download_url:
                 return jsonify({'status': 'error', 'message': 'Video found but no download link available.'}), 500

            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Galactic Video'),
                'thumbnail': info.get('thumbnail', ''),
                'download_url': download_url
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    return jsonify({'status': 'success', 'message': 'Message received'})
