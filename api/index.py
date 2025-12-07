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
# Enable CORS for ALL routes and ALL origins
CORS(app, resources={r"/*": {"origins": "*"}})

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
            # Manually add CORS header just in case
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Contact route
@app.route('/api/contact', methods=['POST'])
def contact():
    response = jsonify({'status': 'success', 'message': 'Message received'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
