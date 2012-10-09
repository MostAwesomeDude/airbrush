#!/usr/bin/env python

from __future__ import with_statement

import logging
import os
import sys

from werkzeug.wsgi import DispatcherMiddleware
from flask import Flask

from airbrush import app as airbrush

interpreter = os.path.expanduser("~/local/bin/python")
if sys.executable != interpreter:
    os.execl(interpreter, interpreter, *sys.argv)

app = Flask(__name__)
app.use_x_sendfile = False

handler = logging.FileHandler("error.log")
handler.setLevel(logging.WARNING)
app.logger.addHandler(handler)

app = DispatcherMiddleware(app, {
    "/h": airbrush,
})

application = app
