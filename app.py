from flask import Flask, render_template, request, redirect, url_for, flash
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secretkey'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'html', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load & simpan JSON
def load_data():
    with open('data/daftar-bab.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open('data/daftar-bab.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# Halaman utama
@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)

# Halaman novel
@app.route('/novel/<filename>')
def novel(filename):
    data = load_data()
    return render_template('novel.html', filename=filename, data=data)

# Halaman manga
@app.route('/manga/<filename>')
def manga(filename):
    data = load_data()
    return render_template('manga.html', filename=filename, data=data)

# Upload bab/chapter
@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        tipe = request.form.get('tipe')   # novel/manga
        title = request.form.get('title')
        file = request.files.get('file')
        images = request.files.getlist('images')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            data = load_data()
            entry = {'title': title, 'file': f'static/uploads/{filename}'}

            if tipe == 'novel':
                data['novel'].append(entry)
            else:
                data['manga'].append(entry)
                # simpan gambar manga
                for img in images:
                    if img and allowed_file(img.filename):
                        img.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(img.filename)))

            save_data(data)
            flash('Berhasil upload!')
            return redirect(url_for('index'))
        else:
            flash('File tidak valid!')
            return redirect(request.url)

    return render_template('upload.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs('data', exist_ok=True)
    # buat JSON kosong jika belum ada
    if not os.path.exists('data/daftar-bab.json'):
        with open('data/daftar-bab.json', 'w', encoding='utf-8') as f:
            f.write('{"novel":[],"manga":[]}')
    app.run(debug=True)

