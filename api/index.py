from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# --- THE DOWNLOAD LOGIC ---
# We use two decorators to ensure it works whether Vercel sends '/api' or not.
@app.route('/api/get-video', methods=['GET'])
@app.route('/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'status': 'error', 'message': 'Please provide a URL'}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'simulate': True, # Vercel cannot save files, so we simulate
            'skip_download': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 1. Get Title
            title = info.get('title', 'Galactic Video')
            
            # 2. Get Thumbnail
            thumbnail = info.get('thumbnail', '')
            
            # 3. Get Direct Download Link
            download_url = info.get('url', None)
            
            # Backup for TikTok/IG where url might be inside 'entries'
            if not download_url and 'entries' in info:
                try:
                    download_url = info['entries'][0].get('url')
                except:
                    pass

            if not download_url:
                 return jsonify({'status': 'error', 'message': 'Could not find a download link. This video might be private or blocked.'}), 500

            return jsonify({
                'status': 'success',
                'title': title,
                'thumbnail': thumbnail,
                'download_url': download_url
            })

    except Exception as e:
        # Return the actual error so we can see what's wrong
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- CONTACT FORM ---
@app.route('/api/contact', methods=['POST'])
@app.route('/contact', methods=['POST'])
def contact():
    return jsonify({'status': 'success', 'message': 'Message received (Simulation)'})

# Run locally
if __name__ == '__main__':
    app.run(debug=True)
