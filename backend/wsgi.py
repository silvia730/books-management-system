from app import app, db
from models import Resource, User, Payment

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run() 