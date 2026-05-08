from flask import Flask, render_template, redirect, url_for, session, request
from werkzeug.utils import secure_filename
import pathlib
import bcrypt
import json
import os

PASSWORD = bcrypt.hashpw("Admin123".encode('utf-8'), bcrypt.gensalt(14))

app = Flask(__name__)
with open('appSecret', 'r') as f:
    app.secret_key = f.read()

def get_settings():
    with open("settings.json", 'r') as f:
        return json.load(f)
    
def save_settings(setting):
    with open("settings.json", 'w') as f:
        json.dump(setting, f, indent=4)

def get_lang(settings):
    with open(os.path.join("lang", f"la{settings['systemLanguage']}.json"), 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    setting = get_settings()
    return render_template("index.html", settings=setting, lang=get_lang(setting))

@app.route('/login')
def login():
    setting = get_settings()
    return render_template("login.html", settings=setting, lang=get_lang(setting))

@app.route('/login_post', methods=['POST'])
def login_post():
    setting = get_settings()
    password = request.form.get('password')

    if bcrypt.checkpw(password.encode('utf-8'), setting['password'].encode('utf-8')):
        session['logged_in'] = True
        return redirect(url_for('settings'))

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/settings')
def settings():
    setting = get_settings()
    
    if session.get('logged_in'):
        return render_template("settings.html", settings=setting, lang=get_lang(setting), langs=[file.stem for file in pathlib.Path('lang').glob('*.json')], pdfs=[file.name for file in pathlib.Path('static').glob('*.pdf')])
    
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    setting = get_settings()
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename != '' and file.filename.endswith('.pdf') and file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('static', filename))
            setting['pdfPath'] = filename
            save_settings(setting)

    return redirect(url_for('settings'))

@app.route('/settings_post', methods=['POST'])
def settings_post():
    systemLanguage = request.form.get('systemLanguage')
    backgroundColor = request.form.get('backgroundColor')
    pdfPath = request.form.get('pdfPath')
    interval = request.form.get('interval')
    port = request.form.get('port')
    password = request.form.get('password')

    print(systemLanguage)

    new_settings = get_settings()
    if (systemLanguage): new_settings['systemLanguage'] = systemLanguage
    if (backgroundColor): new_settings['backgroundColor'] = backgroundColor
    if (pdfPath): new_settings['pdfPath'] = pdfPath
    if (interval): new_settings['interval'] = interval
    if (port): new_settings['port'] = port
    if (password): new_settings['password'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode()

    save_settings(new_settings)

    return redirect(url_for('settings'))

if __name__ == "__main__":
    setting = get_settings()
    if not setting['password']: setting['password'] = PASSWORD.decode()
    save_settings(setting)

    app.run(host="0.0.0.0", port=setting['port'], debug=False)