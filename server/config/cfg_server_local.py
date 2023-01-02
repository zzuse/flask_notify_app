import os


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True

    DEVICE_MANAGER_LOG = os.path.join(BASE_DIR, 'log/server.log')
    DB_VERSION = "1.22"

    # The time that report should move to history report table.(days)
    REPORT_TABLE_MOVE_TO_HISTORY_TABLE = 30

    DEFAULT_MAIL = []

    PSW_FOR_DELETE = 'cHBnLXFhMTIzNDU2'

    LOCAL_USER_PASSWORD = "password"

    REPORT_SERVER = "http://127.0.0.1:5001"
    REPORT_PRODUCER_SERVICE = "/api/report_producer/"
