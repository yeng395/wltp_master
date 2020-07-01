from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(Config)

from app import routes

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080,debug=True)