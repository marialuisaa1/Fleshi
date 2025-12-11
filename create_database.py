from appfleshi import database, app
from appfleshi.models import User, Photo,Like

with app.app_context():
    database.create_all()
