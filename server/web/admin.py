from flask_admin.contrib.sqla import ModelView
from flask import (
    g, session
)


class PPModelView(ModelView):
    def is_accessible(self):
        if g.user:
            return session['user_name'] == 'root'
        return False
