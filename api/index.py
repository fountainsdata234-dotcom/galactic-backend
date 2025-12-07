from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import ssl
import certifi
import os

# --- THE NUCLEAR SSL FIX ---
# This forces Python to ignore missing certificates on Vercel's server
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

app = Flask(__name__)
CORS(app)

@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    try:
        # Optimization for Vercel
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            # CRITICAL: We explicitly tell yt-dlp to ignore SSL errors
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'simulate': True, 
            'skip_download': True,
            # Use a generic user agent to look like a real browser
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Smart URL extraction
            download_url = info.get('url', None)
            
            # Fallback for complex sites
            if not download_url and 'entries' in info:
                try:
                    download_url = info['entries'][0].get('url')
                except:
                    pass

            if not download_url:
                 # If we have a title but no URL, it might be a restricted video
                 if info.get('title'):
                     return jsonify({'status': 'error', 'message': 'Video found, but download link is protected/encrypted.'}), 500
                 return jsonify({'status': 'error', 'message': 'Could not extract link.'}), 500

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

# Local testing
if __name__ == '__main__':
    app.run(debug=True)
