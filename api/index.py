from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Galactic Backend is Running!"

@app.route('/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # VERCEL OPTIMIZED OPTIONS
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            # CRITICAL: Vercel only allows writing to /tmp/ folder
            'cache_dir': '/tmp/',
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'geo_bypass': True,
            # User agent to look like a real browser
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info
            info = ydl.extract_info(url, download=False)
            
            # Handle different JSON structures (Shorts vs Video vs TikTok)
            video_url = info.get('url', None)
            
            # If direct URL is missing, check formats (common in YouTube)
            if not video_url and 'formats' in info:
                # Find best format that contains video
                best_format = None
                for f in info['formats']:
                    if f.get('url'):
                        best_format = f['url']
                        # We prefer mp4
                        if f.get('ext') == 'mp4':
                            video_url = f['url']
                # Fallback to the last found url if specific mp4 logic fails
                if not video_url:
                    video_url = best_format

            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Video Content'),
                'thumbnail': info.get('thumbnail', ''),
                'download_url': video_url,
                'platform': info.get('extractor_key', 'Unknown')
            })

    except Exception as e:
        # This will now print the EXACT error to your browser console
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500

# Vercel needs this for WSGI
app = app
