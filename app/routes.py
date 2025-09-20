from flask import render_template, redirect
from app import app
import re

def extract_key(line):
    return re.search("\"[^\"]+\"", line)

@app.route("/")
@app.route("/index")
def index():
    return redirect('/chat')

@app.route("/search")
@app.route("/chat")
def chat():
    keys_file = open('keys.txt', 'r')
    
    gemini_key = extract_key(keys_file.readline())
    if gemini_key is None:
        raise Exception("GEMINI_API_KEY not found in keys file")
    else:
        gemini_key = gemini_key.group(0)[1:-1]

    google_key = extract_key(keys_file.readline())    
    if google_key is None:
        raise Exception("GOOGLE_API_KEY not found in keys file")
    else:
        google_key = google_key.group(0)[1:-1]
        
    google_id = extract_key(keys_file.readline())
    if google_id is None:
        raise Exception("SEARCH_ENGINE_ID not found in keys file")
    else:
        google_id = google_id.group(0)[1:-1]
        
    return render_template('chat.html', gem_key=gemini_key, ggl_key=google_key, ggl_id=google_id)