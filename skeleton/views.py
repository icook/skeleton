import os

from flask import render_template, Blueprint, send_from_directory

from . import root


main = Blueprint('main', __name__)


@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(root, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@main.route("/")
def home():
    return render_template('home.html')
