from flask import Flask
from flask.ext.holster.main import init_holster
from flask.ext.holster.simple import html

from wonders.wonders import Wonders

app = Flask(__name__)
init_holster(app)

w = Wonders("wonders/wonders.txt")

@app.holster("/wonders")
@app.holster("/wonders/<int:n>")
@html("wonders.html")
def wonders(n=None):
    if n is None:
        effect = w.random()
    else:
        effect = w.get(n)
    return {
        "effect": effect,
        "number": n,
    }
