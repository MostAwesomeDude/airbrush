from flask import Flask
from flask.ext.holster.main import init_holster
from flask.ext.holster.simple import html

app = Flask(__name__)
init_holster(app)

@app.holster("/wonders")
@html("wonders.html")
def wonders():
    return {}
