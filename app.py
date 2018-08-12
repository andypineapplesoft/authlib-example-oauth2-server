from website.app import create_app
import ssl


application = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:root@localhost/oauth?charset=utf8',
})

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)

@application.cli.command()
def initdb():
    from website.models import db
    db.create_all()
