from flask import render_template, redirect
from app import app

@app.route("/")
@app.route("/index")
def index():
    return redirect('/chat')

@app.route("/search")
@app.route("/chat")
def chat():
    return render_template('chat.html')