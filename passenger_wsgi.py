#!/usr/bin/env python

from __future__ import with_statement

import os
import sys

from flask import Flask

interpreter = os.path.expanduser("~/local/bin/python")
if sys.executable != interpreter:
    os.execl(interpreter, interpreter, *sys.argv)

app = Flask(__name__)
app.use_x_sendfile = False

if __name__ == "__main__":
    app.run(debug=True)
else:
    application = app
    import logging
    handler = logging.FileHandler("error.log")
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)
