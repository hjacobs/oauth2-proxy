============
OAuth2 Proxy
============

Flask application to serve static files to authenticated users (via OAuth 2 authorization flow).

.. code-block:: bash

    $ sudo pip3 install -r requirements.txt
    $ python3 -m oauth2_proxy.app

Environment Variables
======================

The following environment variables can be used for configuration:

``APP_ROOT_DIR``
    Directory to serve files from.
``APP_SECRET_KEY``
    Random secret key to sign the session cookie.
``APP_URL``
    Base URL of the application (needed for OAuth 2 redirect).
``CREDENTIALS_DIR``
    Directory containing client.json

