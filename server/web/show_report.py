from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from server.web.auth import login_required
from server.database.db_manager import g_dbm

report_bp = Blueprint('report', __name__, url_prefix='/report', template_folder="templates")


@report_bp.route('/')
def index():
    user_name = session['user_name']
    print(user_name)
    posts = g_dbm.query_report_by_group_like(g.user['user_group'])
    return render_template('report/info.html', posts=posts)


"""TODO query_report_by_status"""
"""TODO query_join_report_info_by_email"""
"""TODO uery_join_report_info_by_id"""


@report_bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = g_dbm.query_report_celeryid(id)
    print(post.CeleryTaskID)
    if request.method == 'POST':
        report_info = dict()
        report_info["CeleryTaskID"] = post.CeleryTaskID
        report_info["TaskID"] = request.form['TaskID']
        report_info["DeviceId"] = request.form['DeviceId']
        report_info["QueueId"] = request.form['QueueId']
        report_info["ContainerId"] = request.form['ContainerId']
        report_info["ParameterList"] = request.form['ParameterList']
        report_info["Status"] = request.form['Status']
        report_info["Description"] = request.form['Description']
        report_info["LogLocation"] = request.form['LogLocation']
        report_info["ReportLocation"] = request.form['ReportLocation']
        report_info["EmailReceiverList"] = request.form['EmailReceiverList']
        report_info["Current"] = request.form['Current']
        report_info["CeleryTaskStartTime"] = post.CeleryTaskStartTime
        report_info["StartRunTime"] = post.StartRunTime
        report_info["LastRunTime"] = post.LastRunTime
        report_info["FailedReason"] = request.form['FailedReason']
        report_info["ResyncPath"] = request.form['ResyncPath']
        report_info["TaskOwner"] = request.form['TaskOwner']
        report_info["Group"] = request.form['Group']
        report_info["StepDuringTime"] = []
        error = None

        if not report_info["TaskOwner"]:
            error = 'TaskOwner name is required.'

        if error is not None:
            flash(error)
        else:
            g_dbm.register_or_update_report(report_info)
            return redirect(url_for('report.index'))

    return render_template('report/update.html', post=post)


@report_bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    g_dbm.delete_report_by_id(id)
    return redirect(url_for('report.index'))
