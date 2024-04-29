from flask import Blueprint, redirect, render_template, request, session

from models.user import User, db

auth_controller = Blueprint('auth_controller', __name__)

@auth_controller.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle form submission
        # Your signup logic here
        return redirect('/login')

    return render_template('signup.html')


@auth_controller.route('/login', methods=['GET', 'POST'])
def login():
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

    return render_template('login.html')


@auth_controller.route('/dashboard', methods=['GET'])
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)

    return redirect('/login')

@auth_controller.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return redirect('/index')
