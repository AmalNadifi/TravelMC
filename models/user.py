from flask_bcrypt import Bcrypt
from models.db import db

bcrypt = Bcrypt()


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(50))
  last_name = db.Column(db.String(50))
  phone = db.Column(db.String(20))
  email = db.Column(db.String(100), unique=True)
  location = db.Column(db.String(100))
  password = db.Column(db.String(100))
  # Trips relationship
  trips = db.relationship('Trip', back_populates='user')

  # Joined trips relationship
  joined_trips = db.relationship('Trip',
                              secondary='trip_participant',
                              back_populates='participants')

  def __init__(self, first_name, last_name, phone, email, location,
               password):
    self.first_name = first_name
    self.last_name = last_name
    self.phone = phone
    self.email = email
    self.location = location
    self.password = bcrypt.generate_password_hash(password).decode('utf-8')

  def check_password(self, password):
      return bcrypt.check_password_hash(self.password, password)
