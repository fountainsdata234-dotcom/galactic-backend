from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Vercel requires the app to be available as 'app'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # This helps debug if routes are wrong
    return jsonify({"message": "API is running. Use /api/get-video"}), 200

@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    try:
        # Optimization for Vercel (Serverless has time limits)
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'simulate': True,  # Do not download file to server
            'skip_download': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Smart URL extraction
            download_url = info.get('url', None)
            if not download_url and 'entries' in info:
                download_url = info['entries'][0].get('url')

            if not download_url:
                 return jsonify({'status': 'error', 'message': 'Could not extract direct link.'}), 500

            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Galactic Video'),
                'thumbnail': info.get('thumbnail', ''),
                'download_url': download_url
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# This allows you to run it locally if needed
if __name__ == '__main__':
    app.run(debug=True)
