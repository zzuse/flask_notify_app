import os


class ServerConfig(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True

    DEVICE_MANAGER_LOG = os.path.join(BASE_DIR, 'log/server.log')

    # The time that report should move to history report table.(days)
    REPORT_TABLE_MOVE_TO_HISTORY_TABLE = 30