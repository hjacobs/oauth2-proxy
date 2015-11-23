============
OAuth2 Proxy
============

.. image:: https://img.shields.io/pypi/dw/oauth2-proxy.svg
   :target: https://pypi.python.org/pypi/oauth2-proxy/
   :alt: PyPI Downloads

.. image:: https://img.shields.io/pypi/v/oauth2-proxy.svg
   :target: https://pypi.python.org/pypi/oauth2-proxy/
   :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/l/oauth2-proxy.svg
   :target: https://pypi.python.org/pypi/oauth2-proxy/
   :alt: License

Flask application to serve static files to authenticated users (via OAuth 2 authorization flow).

.. code-block:: bash

    $ sudo pip3 install -r requirements.txt
    $ python3 -m oauth2_proxy.app

Environment Variables
======================

The following environment variables can be used for configuration:

``APP_DEBUG``
    Enable debug output via HTTP by setting this property to ``true``. Do not set this flag in production.
``APP_ROOT_DIR``
    Directory to serve static files from.
``APP_SECRET_KEY``
    Random secret key to sign the session cookie.
``APP_URL``
    Base URL of the application (needed for OAuth 2 redirect).
``CREDENTIALS_DIR``
    Directory containing client.json

