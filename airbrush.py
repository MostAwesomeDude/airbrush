from flask import Flask, abort
from flask.ext.holster.main import init_holster
from flask.ext.holster.simple import html

from wonders.wonders import Wonders, prettify

app = Flask(__name__)
app.debug = True
init_holster(app)

w = Wonders()
w.load_wonders("wonders/wonders.txt")

@app.holster("/wonders")
@app.holster("/wonders/<int:n>")
@html("wonders.html")
def wonders(n=None):
    if n is None:
        n, effect = w.random()
    else:
        # Switch from zero-indexed to one-indexed.
        n -= 1

        if 0 <= n < len(w.wonders):
            effect = w.wonders[n]
        else:
            abort(404)

    # And back to one-indexed.
    n += 1

    return {
        "effect": prettify(effect),
        "number": n,
    }
