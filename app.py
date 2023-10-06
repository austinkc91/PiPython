import os
import platform
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import subprocess
import signal

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'py'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = 'supersecretkey'  # Set a secret key for flash messages

# Ensure the UPLOAD_FOLDER exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])

script_process = None

def allowed_file(filename):
    return filename.lower().endswith('.py')

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully!', 'success')
    else:
        flash('Invalid file format!', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            flash(f'{filename} deleted successfully!', 'success')
        else:
            flash(f'{filename} not found!', 'error')
    except Exception as e:
        flash(f'Error deleting {filename}: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/run', methods=['POST'])
def run():
    global script_process
    filename = request.form['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        script_process = subprocess.Popen(['python', filepath])
        flash('Script started successfully!', 'success')
    except Exception as e:
        flash(f'Error starting script: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop():
    global script_process
    try:
        if script_process:
            script_process.terminate()  # Terminate the script process
            script_process = None  # Set it to None after termination
            flash('Script stopped successfully!', 'success')
    except Exception as e:
        flash(f'Error stopping script: {str(e)}', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True  # Enable debugging mode
    app.run(host='0.0.0.0', port=5000)
