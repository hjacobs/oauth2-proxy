#!/usr/bin/env python3

import json
import logging
import os
from flask import Flask, redirect, url_for, session, request, send_from_directory
from flask_oauthlib.client import OAuth


app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv('APP_SECRET_KEY', 'development')
oauth = OAuth(app)

with open(os.path.join(os.getenv('CREDENTIALS_DIR', ''), 'client.json')) as fd:
    client_credentials = json.load(fd)

auth = oauth.remote_app(
    'auth',
    consumer_key=client_credentials['client_id'],
    consumer_secret=client_credentials['client_secret'],
    request_token_params={'scope': 'uid'},
    base_url='https://auth.zalando.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://auth.zalando.com/oauth2/access_token',
    authorize_url='https://auth.zalando.com/oauth2/authorize?realm=employees'
)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if 'auth_token' in session:
        return send_from_directory('./', path)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return auth.authorize(callback=os.getenv('APP_URL', '').rstrip('/') + '/login/authorized')


@app.route('/logout')
def logout():
    session.pop('auth_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = auth.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['auth_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))


@auth.tokengetter
def get_auth_oauth_token():
    return session.get('auth_token')


# WSGI application
application = app

if __name__ == '__main__':
    # development mode: run Flask dev server
    logging.basicConfig(level=logging.DEBUG)
    app.run()
