import datetime
import os
import uuid

from flask import Blueprint, abort, redirect, render_template, request, session, flash, url_for
from flask_wtf.csrf import generate_csrf, validate_csrf
from flask import jsonify

from models.trip import Trip, db
from models.user import User
from utils.allowed_files import allowed_file

UPLOAD_FOLDER = './static/uploads'

trip_controller = Blueprint('trip_controller', __name__)


@trip_controller.route('/trips/create', methods=['GET', 'POST'])
def create():
  user = get_user()
  if not user:
    return redirect('/login')

  filename = None  # Initialize filename outside the if block

  if request.method == 'POST':
    file = request.files['image']

    if file and file.filename is not None and allowed_file(file.filename):
      filename, ext = os.path.splitext(file.filename)
      random_filename = str(uuid.uuid4()) + ext
      file.save(os.path.join(UPLOAD_FOLDER, random_filename))

    new_trip = Trip(
      title=request.form['title'],
      destination=request.form['destination'],
      start_date=datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
      end_date=datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
      description=request.form.get('description'),
      image=os.path.join(UPLOAD_FOLDER, random_filename) if random_filename else None,
      user_id=user.id
    )

    db.session.add(new_trip)
    db.session.commit()
    return redirect('/trips/owned_trips')

  return render_template('trip/create.html', user=user)


@trip_controller.route('/trips', methods=['GET'])
def trips():
  user = get_user()
  if not user:
    return redirect('/login')
  trip_list = Trip.query.filter(Trip.user_id != user.id).all()
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
      'participants': trip.participants,
      'user': trip.user
    })

  return render_template('trip/index.html', user=user, trips=trips)


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

  return render_template('trip/index.html', trip_content=trip_content)


@trip_controller.route('/trips/edit/<int:trip_id>', methods=['GET', 'POST'])
def edit_trip(trip_id):
  user = get_user()
  if not user:
    return redirect('/login')
  trip = Trip.query.get_or_404(trip_id)
  if trip.user is user:
    if request.method == 'POST':
      trip.title = request.form['title']
      trip.destination = request.form['destination']
      trip.start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
      trip.end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
      trip.description = request.form.get('description')
      file = request.files['image']
      if file and file.filename is not None and allowed_file(file.filename):
        filename, ext = os.path.splitext(file.filename)
        random_filename = str(uuid.uuid4()) + ext
        file.save(os.path.join(UPLOAD_FOLDER, random_filename))
        trip.image = os.path.join(UPLOAD_FOLDER, random_filename) if random_filename else None
      db.session.commit()
      flash('the trip has been updated successfully', 'success')
      return redirect('/trips/owned_trips')
    elif request.method == 'GET' :
      trip_content = {
              'id': trip.id,
              'title': trip.title,
              'destination': trip.destination,
              'start_date': str(trip.start_date),
              'end_date': str(trip.end_date),
              'description': trip.description,
              'participants': trip.participants,
              'image': trip.image,
              'user': trip.user,
              'trip': trip
          }
      return render_template('trip/edit.html', trip_content=trip_content, user=user)
    else:
      flash('you are not authorized to delete this trip', 'warning')
    return redirect('/trips/owned_trips')
      

@trip_controller.route('/trips/<int:trip_id>', methods=['POST', 'DELETE'])
def delete_trip(trip_id):
  user = get_user()
  if not user:
    return redirect('/login')
  trip = Trip.query.get_or_404(trip_id)
  if trip.user is user:
    db.session.delete(trip)
    db.session.commit()
    flash('the trip has been deleted successfully', 'success')
  else:
    flash('you are not authorized to delete this trip', 'warning')
  return redirect('/trips/owned_trips')


@trip_controller.route('/trips/join_trip/<int:trip_id>', methods=['GET'])
def join_trip(trip_id):
  user = get_user()
  if not user:
    return redirect('/login')

  trip = Trip.query.get_or_404(trip_id)
  if (user is trip.user):
    flash('User is the owner of this trip can\'t be joined to it!', 'warning')
  elif user in trip.participants:
    trip.participants.remove(user)
    db.session.commit()
    flash('User removed successfully!', 'danger')
  else: 
    trip.participants.append(user)
    db.session.commit()
    flash('User joined successfully!', 'success')
  return redirect('/trips')

@trip_controller.route('/trips/owned_trips', methods=['GET'])
def get_all_my_trips():
  user = get_user()
  if not user:
    return redirect('/login')

  trip_list = Trip.query.filter_by(user=user).all()
  # print("user", trip_list)
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
      'participants': trip.participants,
      'user': trip.user
    })

  return render_template('trip/owned_trip.html', user=user, trips=trips)


def get_user():
  if 'email' in session:
    return User.query.filter_by(email=session['email']).first()
  return None
