from flask import Flask
app = Flask(__name__)

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
