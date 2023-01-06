from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from server.database.db_manager import g_dbm

index_bp = Blueprint('index', __name__, template_folder="templates")


@index_bp.route('/')
@index_bp.route('/index')
def index():
    return render_template('index.html')
