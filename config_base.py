import os

pw = os.environ['CC_MYSQL_PW']
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="alexjohnson84",
    password=pw,
    hostname="alexjohnson84.mysql.pythonanywhere-services.com",
    databasename="alexjohnson84$cribdb",
)
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
