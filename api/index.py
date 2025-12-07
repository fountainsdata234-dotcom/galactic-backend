from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
CORS(app)

# --- ROUTE 1: VIDEO DOWNLOADER ---
@app.route('/api/get-video', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    try:
        # Configuration to make yt-dlp fast and lightweight for Vercel
        ydl_opts = {
            'format': 'best', # Get best quality
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            # IMPORTANT: Vercel kills processes after 10s. We cannot download the file.
            # We only extract the URL.
            'simulate': True, 
            'skip_download': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract safe title
            title = info.get('title', 'Galactic Video')
            
            # Find the best download link
            download_url = info.get('url', None)
            
            # Some sites (like TikTok) return url in different fields
            if not download_url and 'entries' in info:
                download_url = info['entries'][0].get('url')
            
            if not download_url:
                 return jsonify({'status': 'error', 'message': 'Could not extract link. Site might be blocking Vercel.'}), 500

            return jsonify({
                'status': 'success',
                'title': title,
                'thumbnail': info.get('thumbnail', ''),
                'download_url': download_url
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- ROUTE 2: CONTACT FORM (EMAIL) ---
@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    name = data.get('name')
    email_from = data.get('email')
    message = data.get('msg')
    
    # You need to set these in Vercel Environment Variables
    # MY_EMAIL = "fountainsdata234@gmail.com"
    # MY_PASSWORD = "your-google-app-password" 
    
    my_email = os.environ.get('MY_EMAIL')
    my_password = os.environ.get('MY_PASSWORD')

    if not my_email or not my_password:
        return jsonify({'error': 'Server Email Config Missing'}), 500

    msg_content = f"Name: {name}\nFrom: {email_from}\n\nMessage:\n{message}"
    msg = MIMEText(msg_content)
    msg['Subject'] = f"GalacticSearch Contact: {name}"
    msg['From'] = my_email
    msg['To'] = my_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(my_email, my_password)
        server.send_message(msg)
        server.quit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For local testing only
if __name__ == '__main__':
    app.run(debug=True)
