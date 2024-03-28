from flask import Flask, request, render_template, flash, redirect, url_for
import requests
import os
from flask_caching import Cache
import logging

app = Flask(__name__)
app.secret_key = os.urandom(16)

app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 1800
cache = Cache(app)

app.logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

app.logger.addHandler(handler)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def search():
    domain = request.form['domain']

    cached_response = cache.get(domain)
    if cached_response:
        app.logger.debug(f"Cache hit for domain {domain}")
        if 'error' in cached_response:
            flash(cached_response['error'], 'error')
            return redirect(url_for('home'))
        else:
            return render_template("result.html", emails=cached_response)

    api_key = os.getenv("HUNTER_API_KEY")
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    response = requests.get(url)
    app.logger.debug(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        emails = data['data']['emails']
        print(emails)
        for email in emails:
            status = verifier(email['value'])
            email['status'] = status
        cache.set(domain, emails)
        app.logger.debug(f"Emails: {emails}")
        return render_template("result.html", emails=emails)
    
    else:
        error_message = 'Unknown response format'
        if 'errors' in response:
            error_messages  = []
            for error in response['errors']:
                error_messages .append(error.get('details', 'Unknown error'))
            error_message = '; '.join(error_messages)
        cache.set(domain, {'error': error_message})
        flash(error_message, 'error')
        return redirect(url_for('home'))
    
def verifier(email):
    api_key = os.getenv("HUNTER_API_KEY")
    
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']['status']
    else:
        return 'Unknown'

@app.route("/test")
def test():
    # response = request.get_json()
    # if 'data' in response:
    #     return render_template("result.html", data=response['data'])
    
    # elif 'errors' in response:
    #     error_messages = []
    #     for error in response['errors']:
    #         error_messages.append(error.get('details', 'Unknown error'))
    #     error_message_str = '; '.join(error_messages)
    #     flash(error_message_str, 'error')
    #     return redirect(url_for('home'))
    # else:
    #     flash('Unknown response format', 'error')
    #     return redirect(url_for('home'))
    emails = [
        {'value': 'example1@example.com', 'type': 'personal', 'confidence': 95, 'status': 'valid'},
        {'value': 'example2@example.com', 'type': 'work', 'confidence': 90, 'status': 'invalid'}
    ]
    return render_template("result.html", emails=emails)