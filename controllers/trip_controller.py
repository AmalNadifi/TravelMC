from datetime import date
import datetime
import os
import uuid
from flask import Blueprint, redirect, render_template, request, session
from werkzeug.utils import secure_filename


from models.trip import Trip, db
from models.user import User
from utils.allowed_files import allowed_file

UPLOAD_FOLDER = '/uploads'

trip_controller = Blueprint('trip_controller', __name__)

@trip_controller.route('/trips/create', methods=['GET', 'POST'])
def create():
    user = get_user()
    if not user:
        return redirect('/login')

    filename = None  # Initialize filename outside the if block

    if request.method == 'POST':
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename, ext = os.path.splitext(file.filename)
            random_filename = str(uuid.uuid4()) + ext
            file.save(os.path.join('/uploads', random_filename))

        new_trip = Trip(
            title=request.form['title'],
            destination=request.form['destination'],
            start_date=datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            description=request.form.get('description'),
            image=os.path.join(UPLOAD_FOLDER, filename) if filename else None,
            user_id=user.id
        )

        db.session.add(new_trip)
        db.session.commit()
        return redirect('/trips')

    return render_template('trip/create.html')


@trip_controller.route('/trips', methods=['GET'])
def get_all_trips():
  user = get_user()
  if not user:
     return redirect('/login')
  trip_list = Trip.query.all()
  trips = []
  for trip in trip_list:
    trips.append({
        'id': trip.id,
        'title': trip.title,
        'destination': trip.destination,
        'start_date': str(trip.start_date),
        'end_date': str(trip.end_date),
        'description': trip.description,
        'image': trip.image,
        'user_id': trip.user_id
    })
  print(trip_list)
  return render_template('trip/index.html', trips=trips)

@trip_controller.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
  user = get_user()
  if not user:
     return redirect('/login')
  trip = Trip.query.get_or_404(trip_id)
  trip_content = {
      'id': trip.id,
      'title': trip.title,
      'destination': trip.destination,
      'start_date': str(trip.start_date),
      'end_date': str(trip.end_date),
      'description': trip.description,
      'image': trip.image,
      'user_id': trip.user_id
  }

  return render_template('trip/read.html', trip_content=trip_content)

@trip_controller.route('/trips/update/<int:trip_id>', methods=['GET', 'PUT'])
def update_trip(trip_id):
  user = get_user()
  if not user:
     return redirect('/login')
  trip = Trip.query.get_or_404(trip_id)
  if (request.method == 'PUT' & user.id == trip.user_id):
    trip.title = request.form['title']
    trip.destination = request.form['destination']
    trip.start_date = request.form['start_date']
    trip.end_date = request.form['end_date']
    trip.description = request.form.get('description')
    trip.image = request.files.get('image')
    db.session.commit()
    return redirect('/trips') 
  return render_template('trip/update.html', trip)

@trip_controller.route('/trips/delete/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
  user = get_user()
  if not user:
     return redirect('/login')
  trip = Trip.query.get_or_404(trip_id)
  if (user.id == trip.user_id):
    db.session.delete(trip)
    db.session.commit()
  return redirect('/trips')

def get_user():
  if 'email' in session:
    return User.query.filter_by(email=session['email']).first()
  return None
