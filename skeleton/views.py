import os
import re
import sqlalchemy

from flask import (render_template, Blueprint, send_from_directory, request,
                   url_for, redirect, current_app)
from flask.ext.login import login_required, logout_user, current_user, login_user

from . import root, db, lm
from .models import User


main = Blueprint('main', __name__)


@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(root, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@main.route("/account")
@login_required
def account():
    return render_template('account.html')


@main.route("/")
def home():
    return render_template('home.html')


@main.route("/register", methods=['GET', 'POST'])
def register():
    errors = []
    if request.method == 'POST':
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", request.form['email']):
            errors.append("Invalid email address provided")
        if not re.match(r"^(?=.*\d)(?=.*[a-zA-Z]).{6,48}$", request.form['password']):
            errors.append("Password must contain at least 6 characters long and have one character and one number")
        if not request.form['password'] == request.form['password-confirm']:
            errors.append("Passwords must match")

        if not errors:
            user = User(email=request.form['email'])
            user.password = request.form['password']
            try:
                db.session.add(user)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                current_app.logger.error("Database comm error", exc_info=True)
                errors.append("That email address is already registered!")
            except Exception:
                current_app.logger.error("Database comm error", exc_info=True)
                errors.append("Unable to communicate with database properly!")
            else:
                login_user(user)
                return redirect(request.args.get("next") or url_for("main.home"))

    return render_template('register.html', errors=errors)


@main.route("/login", methods=['GET', 'POST'])
def login():
    errors = []
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if not user.check_password(request.form['password']):
                errors.append("Incorrect email/password")
            else:
                login_user(user)
                return redirect(request.args.get("next") or url_for("main.home"))
        else:
            errors.append("Incorrect email/password")
    return render_template('login.html', errors=errors)


@main.route("/activate/<hash>/<userid>", methods=['GET', 'POST'])
def activate():
    pass


@main.route("/recover/<hash>/<userid>", methods=['GET', 'POST'])
def recover():
    pass


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@lm.user_loader
def load_user(userid):
    try:
        return User.query.filter_by(id=userid).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None
