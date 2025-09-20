from flask import render_template
from app import app

@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'bproteau0'}
    return render_template('index.html', title='WTN Assistant', user=user)