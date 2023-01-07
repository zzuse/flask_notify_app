from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from server.web.auth import login_required
from server.database.db_manager import g_dbm

task_bp = Blueprint('task', __name__, url_prefix='/task', template_folder="templates")


@task_bp.route('/')
def index():
    user_name = session['user_name']
    print(user_name)
    posts = g_dbm.query_tasks_by_name("default")
    return render_template('task/info.html', posts=posts)


@task_bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(ids):
    post = g_dbm.query_task_by_id(ids)
    print(post.ID)
    if request.method == 'POST':
        task_info = dict()
        task_info["ID"] = post.ID
        task_info["Alias"] = request.form['Alias']
        task_info["Type"] = request.form['Type']
        task_info["CreatedTime"] = request.form['CreatedTime']

        error = None
        if error is not None:
            flash(error)
        else:
            g_dbm.register_or_update_task(task_info)
            return redirect(url_for('task.index'))

    return render_template('task/update.html', post=post)


@task_bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    g_dbm.delete_task_by_id(id)
    return redirect(url_for('task.index'))
