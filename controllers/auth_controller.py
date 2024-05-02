from flask import Blueprint, redirect, render_template, request, session
from utils.allowed_files import allowed_file
import os
import uuid

from models.user import User, db

UPLOAD_FOLDER = './static/uploads'

auth_controller = Blueprint('auth_controller', __name__)

@auth_controller.route('/signup', methods=['GET', 'POST'])
def signup():
  user = get_user()
  if user is not None:
    return redirect('/dashboard')
  if request.method == 'POST':
    first_name = request.form['first_name']
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    email = request.form['email']
    location = request.form.get('location')
    password = request.form['password']
    password2 = request.form['password2']
    file = request.files['image']

    if file and file.filename is not None and allowed_file(file.filename):
      filename, ext = os.path.splitext(file.filename)
      random_filename = str(uuid.uuid4()) + ext
      file.save(os.path.join(UPLOAD_FOLDER, random_filename))
      image = os.path.join(UPLOAD_FOLDER, random_filename) if random_filename else None

    # Validate the password
    if password != password2:
      return render_template('signup.html', error='Passwords do not match')

    # Create a new user
    new_user = User(first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    location=location,
                    password=password,
                    image=image)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect('/login')

  return render_template('signup.html')


@auth_controller.route('/login', methods=['GET', 'POST'])
def login():
  user = get_user()
  if user is not None:
    return redirect('/dashboard')
  if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']

      user = User.query.filter_by(email=email).first()

      if user and user.check_password(password):
          session.permanent = True  # Corrected attribute name
          session['email'] = user.email
          return redirect('/dashboard')
      else:
          return render_template('login.html', error='Invalid user')

  return render_template('login.html', user=user)


@auth_controller.route('/dashboard', methods=['GET'])
def dashboard():
  user = get_user()
  if not user:
    return redirect('/login')
  return render_template('dashboard.html', user=user)

@auth_controller.route('/logout', methods=['POST'])
def logout():
  session.pop('email', None)
  return redirect('/index')

def get_user():
  if 'email' in session:
    return User.query.filter_by(email=session['email']).first()
  return None
