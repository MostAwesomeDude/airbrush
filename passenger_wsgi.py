#!/usr/bin/env python
# Copyright (C) 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import with_statement

import logging
import os
import sys

from werkzeug.wsgi import DispatcherMiddleware
from flask import Flask

from airbrush.main import app as airbrush

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
