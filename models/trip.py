from models.db import db


# Trip Model
class Trip(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  destination = db.Column(db.String(100), nullable=False)
  start_date = db.Column(db.Date, nullable=False)
  end_date = db.Column(db.Date, nullable=False)
  description = db.Column(db.Text)
  image = db.Column(db.String(255))

  # User relationship
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  user = db.relationship('User', back_populates='trips')

  # Join relationship for other users
  participants = db.relationship('User',
                                 secondary='trip_participant',
                                 back_populates='joined_trips')

  def __init__(self, title, destination, start_date, end_date, description,
               image, user_id):
    self.title = title
    self.destination = destination
    self.start_date = start_date
    self.end_date = end_date
    self.description = description
    self.image = image
    self.user_id = user_id


# Association table for participants
trip_participant = db.Table(
    'trip_participant',
    db.Column('trip_id',
              db.Integer,
              db.ForeignKey('trip.id'),
              primary_key=True),
    db.Column('user_id',
              db.Integer,
              db.ForeignKey('user.id'),
              primary_key=True))
