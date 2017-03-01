from flask import Flask
import os

# the app
app = Flask(__name__) # create the application instance

import dotateams.routes
import dotateams.db
import dotateams.user_api

app.config.from_object(__name__) # load config from this file , dotateams.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'dotateams.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('DOTATEAMS_SETTINGS', silent=True)