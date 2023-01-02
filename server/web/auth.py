import functools
from flask import (
    Blueprint, flash, redirect, g, render_template, request, session, url_for
)
from server.database.db_manager import g_dbm
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from server.config.env import Env

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        group = request.form['group']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif g_dbm.query_user_by_name(username) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            g_dbm.register_user_by_name(username, generate_password_hash(password), email, group)
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


def auto_register(oauth_name, oauth_email, oauth_group):
    username = oauth_name
    password = "false_password"
    email = oauth_email
    group = oauth_group
    error = None

    if not username:
        error = 'Username is required.'
        print("error {}\n----------".format(error))
    elif not password:
        error = 'Password is required.'
        print("error {}\n----------".format(error))
    elif g_dbm.query_user_by_name(username) is not None:
        error = 'User {} is already registered.'.format(username)
        print("error {}\n----------".format(error))

    if error is None:
        g_dbm.register_user_by_name(username, generate_password_hash(password), email, group)
        return None
    return "auto register error"


@auth_bp.route('/admin_login', methods=('GET', 'POST'))
def admin_login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = g_dbm.query_user_by_name(username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['user_pass'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_name'] = user['user_name']
            return redirect(url_for('admin.index'))

        flash(error)
    return render_template('auth/admin_login.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    code = request.args.get("code", default="")
    nl = request.args.get("next", default="")
    print("code: {}".format(code))
    print("next: {}".format(nl))

    if code:
        data = {
            "client_id" : "auto",
            "client_secret": "4774051054274",
            "code" : code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://automation.xxx-inc.com:5000/auth/login"
        }
        r1 = requests.post("https://accounts.xxx-inc.com/oauth2/token", data=data).json()
        print("r1 {}\n----------".format(r1))
        access_token = r1["access_token"]
        data2 = {"token": access_token}
        r2 = requests.post("https://accounts.xxx-inc.com/oauth2/get_info", data=data2).json()
        print("r2 {}\n----------".format(r2))
        username = r2["username"]
        print("username {}\n----------".format(username))
        oauth_email = r2["email"]
        oauth_group = r2["groups"][0]
        if username:
            error = None
            user = g_dbm.query_user_by_name(username)
            if user is None:
                error = 'Not exist, auto register username.'
                print("error {}\n----------".format(error))
                error = auto_register(username, oauth_email, oauth_group)
                user = g_dbm.query_user_by_name(username)
            if error is None:
                session.clear()
                session['user_name'] = user['user_name']
                return redirect(url_for('index'))
            return redirect(url_for('index'))
        else:
            return redirect("https://accounts.xxx-inc.com/oauth2/authorize?client_id=auto&response_type=code")
    else:
        return redirect("https://accounts.xxx-inc.com/oauth2/authorize?client_id=auto&response_type=code")


@auth_bp.before_app_request
def load_logged_in_user():
    user_name = session.get('user_name')
    g.env = Env
    if user_name is None:
        g.user = None
    else:
        g.user = g_dbm.query_user_by_name(user_name)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view