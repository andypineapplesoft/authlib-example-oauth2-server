from website.app import create_app


app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:root@localhost/oauth?charset=utf8',
#    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})

def initdb():
    from website.models import db
    db.create_all()
