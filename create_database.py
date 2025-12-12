from appfleshi import database, app
from appfleshi.models import User, Photo

with app.app_context():
    database.create_all()
