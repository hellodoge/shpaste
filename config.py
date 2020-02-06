import os


class Configuration(object):
    DEBUG = True
    SITE_URL = os.environ.get('SITE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    REPO_URL = os.environ.get('REPO_URL')
