from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from server.web.auth import login_required
from server.database.db_manager import g_dbm

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/')
def index():
    """
    show groups depend on user belonging groups
    :return: template
    """
    user_name = session['user_name']
    print(user_name)
    posts = g_dbm.query_user_by_group_like(g.user['user_group'])
    if not posts:
        return redirect(url_for('index'))
    return render_template('user/info.html', posts=posts)


@user_bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = g_dbm.query_user_by_id(id)
    print(post)
    # user = g_dbm.query_user_by_name(session['user_name'])
    post.user_group = g_dbm.query_group_by_name(g.user['user_group'])
    print(post.user_group)
    if request.method == 'POST':
        user_info = dict()
        user_info["user_id"] = post.user_id
        user_info["user_name"] = request.form["user_name"]
        user_info["user_pass"] = post.user_pass
        user_info["user_email"] = request.form["user_email"]
        user_info["user_group"] = ','.join(request.form.getlist('user_group'))
        error = None
        print("update user group!!! -- {}".format(request.form.getlist('user_group')))
        if user_info["user_group"] == "":
            user_info["user_group"] = "Default"

        if not user_info["user_name"]:
            error = 'alias name is required.'

        if error is not None:
            flash(error)
        else:
            g_dbm.update_user_by_id(user_info)
            return redirect(url_for('user.index'))

    return render_template('user/update.html', post=post)


@user_bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    g_dbm.delete_user_by_id(id)
    return redirect(url_for('user.index'))
