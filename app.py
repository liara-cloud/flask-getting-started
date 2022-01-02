import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = './uploads'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/upload')
def upload_index():
    path = os.getcwd()+"/uploads"
    files = []
    for filename in os.listdir(path):
        files.append(filename)
    return render_template('upload.html', files=files)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload_index'))


@app.route('/uploads/<name>')
def download_file(name):
    path = os.getcwd() + '/uploads/' + name
    return send_file(path, as_attachment=True)