from flask import (
    g, session
)


class PPModelView(object):
    def is_accessible(self):
        if g.user:
            return session['user_name'] == 'root'
        return False
