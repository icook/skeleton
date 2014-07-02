import subprocess
import logging
import os
#import cryptacular.bcrypt
import yaml
import sys

from babel.dates import format_datetime
from flask import Flask
#from flask.ext.sqlalchemy import SQLAlchemy
#from flask.ext.login import LoginManager
#from flask.ext.cache import Cache
from jinja2 import FileSystemLoader
from datetime import datetime, timedelta


root = os.path.abspath(os.path.dirname(__file__) + '/../')
#lm = LoginManager()
#db = SQLAlchemy()
#cache = Cache()

#crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


def create_app(config='/config.yml'):
    # initialize our flask application
    app = Flask(__name__, static_folder='../static', static_url_path='/static')

    # set our template path and configs
    app.jinja_loader = FileSystemLoader(os.path.join(root, 'templates'))
    config_vars = yaml.load(open(root + config))
    # inject all the yaml configs
    app.config.update(config_vars)
    app.logger.info(app.config)

    # add the debug toolbar if we're in debug mode...
    if app.config['DEBUG']:
        class LoggerWriter:
            def __init__(self, logger, level):
                self.logger = logger
                self.level = level

            def write(self, message):
                if message != '\n':
                    self.logger.log(self.level, message)

        sys.stdout = LoggerWriter(app.logger, logging.INFO)
        sys.stderr = LoggerWriter(app.logger, logging.INFO)
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
        app.logger.handlers[0].setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(filename)s:%(lineno)d]'))

    # register all our plugins
    #db.init_app(app)
    #cache_config = {'CACHE_TYPE': 'redis'}
    #cache_config.update(app.config.get('main_cache', {}))
    #cache.init_app(app, config=cache_config)
    #lm.init_app(app)

    hdlr = logging.FileHandler(app.config.get('log_file', 'webserver.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    app.logger.addHandler(hdlr)
    app.logger.setLevel(logging.INFO)

    # try and fetch the git version information
    try:
        output = subprocess.check_output("git show -s --format='%ci %h'",
                                         shell=True).strip().rsplit(" ", 1)
        app.config['hash'] = output[1]
        app.config['revdate'] = output[0]
    # celery won't work with this, so set some default
    except Exception:
        app.config['hash'] = ''
        app.config['revdate'] = ''

    # filters for jinja
    @app.template_filter('duration')
    def time_format(seconds):
        # microseconds
        if seconds > 3600:
            return "{}".format(timedelta(seconds=seconds))
        if seconds > 60:
            return "{:,.2f} mins".format(seconds / 60.0)
        if seconds <= 1.0e-3:
            return "{:,.4f} us".format(seconds * 1000000.0)
        if seconds <= 1.0:
            return "{:,.4f} ms".format(seconds * 1000.0)
        return "{:,.4f} sec".format(seconds)

    @app.template_filter('time_ago')
    def pretty_date(time=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        now = datetime.utcnow()
        if type(time) is int:
            diff = now - datetime.utcfromtimestamp(time)
        elif isinstance(time, datetime):
            diff = now - time
        elif not time:
            diff = now - now
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                return str(second_diff / 60) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(second_diff / 3600) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff/7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff/30) + " months ago"
        return str(day_diff/365) + " years ago"

    @app.template_filter('datetime')
    def jinja_format_datetime(value, fmt='medium'):
        if fmt == 'full':
            fmt = "EEEE, MMMM d y 'at' HH:mm"
        elif fmt == 'medium':
            fmt = "EE MM/dd/y HH:mm"
        return format_datetime(value, fmt)

    # Route registration
    # =========================================================================
    from . import views
    app.register_blueprint(views.main)
    #app.register_blueprint(api.api, url_prefix='/api')

    return app
