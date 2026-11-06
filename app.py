from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import yt_dlp

app = Flask(__name__)
UPLOAD_FOLDER = 'downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# 1. Havola (Link) orqali ijtimoiy tarmoqlardan video yuklab olish
@app.route('/download-url', methods=['POST'])
def download_url():
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"success": False, "error": "Iltimos, video havolasini kiriting!"}), 400

    ydl_opts = {
        'outtmpl': os.path.join(UPLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.basename(ydl.prepare_filename(info))
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 2. Kompyuterdan fayl yuklab olish
@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Fayl topilmadi!"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Fayl tanlanmadi!"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return jsonify({"success": True, "filename": file.filename})

# Yuklangan videoni ko'chirib olish yoki ko'rish uchun
@app.route('/downloads/<path:filename>')
def downloaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
