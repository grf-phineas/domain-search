from flask import Flask, request, render_template, flash, redirect, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def search():
    domain = request.form['domain']
    api_key = os.getenv("HUNTER_API_KEY")
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        data = response.json()
        return render_template("result.html", data=data['data'])
    elif 'errors' in response:
        error_messages = []
        for error in response['errors']:
            error_messages.append(error.get('details', 'Unknown error'))
        error_message_str = '; '.join(error_messages)
        flash(error_message_str, 'error')
        return redirect(url_for('home'))
    else:
        flash('Unknown response format', 'error')
        return redirect(url_for('home'))
    

@app.route("/test", methods=["POST"])
def test():
    response = request.get_json()
    if 'data' in response:
        return render_template("result.html", data=response['data'])
    
    elif 'errors' in response:
        error_messages = []
        for error in response['errors']:
            error_messages.append(error.get('details', 'Unknown error'))
        error_message_str = '; '.join(error_messages)
        flash(error_message_str, 'error')
        return redirect(url_for('home'))
    else:
        flash('Unknown response format', 'error')
        return redirect(url_for('home'))