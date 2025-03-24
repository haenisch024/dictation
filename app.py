from flask import Flask, request, render_template, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dictation_pkg.dictation import transcribe_audio_file  # Ensure this function is added in your dictation code

app = Flask(__name__) 
auth = HTTPBasicAuth()
users = { "haenisch024": generate_password_hash("6534") }

@auth.verify_password 
def verify_password(username, password): 
    if username in users and check_password_hash(users.get(username), password): return username

@app.route('/') 
@auth.login_required 
def index(): 
    return render_template("index.html")

@app.route('/upload', methods=['POST']) 
@auth.login_required 
def upload(): 
    # Retrieve meeting agenda (may be blank) 
    agenda = request.form.get('agenda', '') 
    if 'audio' not in request.files: 
        return jsonify({"error": "No audio file provided"}), 400 
    audio_file = request.files['audio'] 
    # Process the audio file with your transcription function 
    transcription = transcribe_audio_file(audio_file) 
    return jsonify({"transcription": transcription, "agenda": agenda})
    
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000)
    