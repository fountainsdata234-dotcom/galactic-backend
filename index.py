from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Galactic Backend is Running on Vercel!"

@app.route('/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Vercel is serverless, so we cannot download large files to disk.
        # We only extract the direct URL.
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            # We use a generic user agent to avoid bot detection
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'download_url': info.get('url', None)
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# For Vercel, we do NOT use app.run()