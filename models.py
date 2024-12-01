from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from utils.uidg import UniqueIDGenerator

db = SQLAlchemy()
bcrypt = Bcrypt()
unique_id_generator = UniqueIDGenerator()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(16), primary_key=True, unique=True, default=unique_id_generator.get_unique_id)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(14), nullable=True)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
