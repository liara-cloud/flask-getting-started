from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_uploaded_files():
    return sorted(os.listdir(app.config['UPLOAD_FOLDER']), reverse=True)

@app.route('/')
def index():
    uploaded_files = get_uploaded_files()
    return render_template('index.html', uploaded_files=uploaded_files)

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{file.filename}")
        file.save(filename)
        file_link = url_for('uploaded_file', filename=os.path.basename(filename))
        success_message = 'File successfully uploaded'
        uploaded_files = get_uploaded_files()
        return render_template('index.html', success=success_message, filename=os.path.basename(filename), file_link=file_link, uploaded_files=uploaded_files)
    else:
        return render_template('index.html', error='Invalid file format')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
