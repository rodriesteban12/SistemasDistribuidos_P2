from flask import Flask
from redis import Redis
import os
import configparser

app = Flask(__name__)

@app.route('/')
def hello():
    Config = configparser.ConfigParser()
    Config.read("variables.conf")
    return 'Hello! {}'.format(
        Config.get("variables", "text"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
