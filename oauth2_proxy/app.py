#!/usr/bin/env python3

import json
import logging
import os
import requests
import flask
from flask import Flask, redirect, url_for, session, request, send_from_directory
from flask_oauthlib.client import OAuth, OAuthRemoteApp
from urllib.parse import urlparse

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.INFO)

sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
sess.mount('http://', adapter)
sess.mount('https://', adapter)

app = Flask(__name__)
app.debug = os.getenv('APP_DEBUG') == 'true'
app.secret_key = os.getenv('APP_SECRET_KEY', 'development')
oauth = OAuth(app)


class OAuthRemoteAppWithRefresh(OAuthRemoteApp):
    '''Same as flask_oauthlib.client.OAuthRemoteApp, but always loads client credentials from file.'''

    def __init__(self, oauth, name, **kwargs):
        # constructor expects some values, so make it happy..
        kwargs['consumer_key'] = 'not-needed-here'
        kwargs['consumer_secret'] = 'not-needed-here'
        OAuthRemoteApp.__init__(self, oauth, name, **kwargs)

    def refresh_credentials(self):
        with open(os.path.join(os.getenv('CREDENTIALS_DIR', ''), 'client.json')) as fd:
            client_credentials = json.load(fd)
        self._consumer_key = client_credentials['client_id']
        self._consumer_secret = client_credentials['client_secret']

    @property
    def consumer_key(self):
        self.refresh_credentials()
        return self._consumer_key

    @property
    def consumer_secrect(self):
        self.refresh_credentials()
        return self._consumer_secret


auth = OAuthRemoteAppWithRefresh(
    oauth,
    'auth',
    request_token_params={'scope': 'uid'},
    base_url='https://auth.zalando.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://auth.zalando.com/oauth2/access_token?realm=employees',
    authorize_url='https://auth.zalando.com/oauth2/authorize?realm=employees'
)
oauth.remote_apps['auth'] = auth

UPSTREAMS = list(filter(None, os.getenv('APP_UPSTREAM', '').split(',')))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if 'auth_token' in session:
        if UPSTREAMS:
            abs_path = '/{}'.format(path.strip('/'))
            for url in UPSTREAMS:
                o = urlparse(url)
                if abs_path.startswith(o.path):
                    parts = flask.request.url.split('/', 3)
                    path_query = parts[-1]
                    upstream_url = '{scheme}://{netloc}/{path}'.format(scheme=o.scheme, netloc=o.netloc,
                                                                       path=path_query)
                    upstream_response = sess.get(upstream_url)
                    headers = {}
                    for key, val in upstream_response.headers.items():
                        if key in set(['Content-Type']):
                            headers[key] = val
                    response = flask.Response(upstream_response.content, upstream_response.status_code, headers)
                    return response
        else:
            # serve static files
            if not path:
                path = 'index.html'
            return send_from_directory(os.getenv('APP_ROOT_DIR', './'), path)
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return 'OK'


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
    print(resp)
    if not isinstance(resp, dict):
        return 'Invalid auth response'
    session['auth_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))


@auth.tokengetter
def get_auth_oauth_token():
    return session.get('auth_token')


# WSGI application
application = app

if __name__ == '__main__':
    # development mode: run Flask dev server
    app.run()
