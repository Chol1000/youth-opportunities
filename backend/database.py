# backend/database.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# These are instance-level objects
db = SQLAlchemy()
bcrypt = Bcrypt()
