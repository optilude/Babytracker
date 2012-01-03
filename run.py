import os

from paste.deploy import loadapp
from gunicorn.app.pasterapp import paste_server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    wsgi_app = loadapp('config:production.ini', relative_to='./src/Babytracker')
    paste_server(wsgi_app, host='0.0.0.0', port=port)
