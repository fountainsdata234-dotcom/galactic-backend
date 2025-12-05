from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Galactic Backend is Stealthy!"

@app.route('/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # STEALTH CONFIGURATION
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'cache_dir': '/tmp/', # Required for Vercel
            
            # TRICK YOUTUBE: Pretend to be an Android Device
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs', 'js'],
                }
            },
            
            # Standard Browser User Agent
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 1. Try to get the direct video url
            video_url = info.get('url', None)
            
            # 2. If no direct url, look for the best format
            if not video_url:
                formats = info.get('formats', [])
                # Filter for mp4s with video and audio
                best_format = next(
                    (f for f in formats if f.get('ext') == 'mp4' and f.get('acodec') != 'none' and f.get('vcodec') != 'none'), 
                    None
                )
                if best_format:
                    video_url = best_format['url']
                else:
                    # Fallback to whatever URL is available
                    video_url = formats[-1]['url'] if formats else None

            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'download_url': video_url,
                'platform': info.get('extractor_key', 'Unknown')
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Vercel Handler
app = app
