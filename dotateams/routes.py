# all the imports
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash

from dotateams import app

import db

# # the app
# app = Flask(__name__) # create the application instance
# app.config.from_object(__name__) # load config from this file , dotateams.py

# # Load default config and override config from an environment variable
# app.config.update(dict(
#     DATABASE=os.path.join(app.root_path, 'dotateams.db'),
#     SECRET_KEY='development key',
#     USERNAME='admin',
#     PASSWORD='default'
# ))
# app.config.from_envvar('DOTATEAMS_SETTINGS', silent=True)

################################
# GENERAL HELPERS
################################

################################
# APPLICATION ROUTING
################################

# Gets the apps homepage
@app.route('/')
def show_teams():
    teams = db.get_all_teams_with_creators_username()
    return render_template('show_teams.html', teams=teams)

# Adds a new team 
@app.route('/add', methods=['GET', 'POST'])
def add_team():
    error = None
    if request.method == 'POST':
        if not request.form.get('title'):
            error = 'Please provide a title'
        elif not request.form.get('description'):
            error = 'Please provide a description'
        else:
            try:
                db.create_new_team(session['user_id'], request.form['title'], request.form['description'])
                flash('New entry was successfully posted')
                return redirect(url_for('profile', username=session['username']))
            except db.OperationException as e:
                error = e.message

    return render_template('add_team.html', error=error, 
        title=request.form.get('title', ''), description=request.form.get('description', ''))

# Log a user in given their username and password
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_one_by_property('user', 'username', username)
        if user:
            if check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = user['id']
                flash('You were logged in')
                return redirect(url_for('show_teams'))
            else:
                error = 'Incorrect password.'
        else:
            error = 'The given username does not exist.'
    return render_template('login.html', error=error)

# Log a user out
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('show_teams'))

# Sign in a new user given a new username and password
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        hashed_pw = generate_password_hash(request.form['password'])

        try:
            new_user_id = db.create_new_user(username, hashed_pw)

            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = new_user_id
            flash('New user successfully created and signed in')
            return redirect(url_for('profile', username=username))
        except db.OperationException as e:
            error = e.message
    return render_template('signup.html', error=error)

# Go to a given user's profile
@app.route('/user/<username>')
def profile(username):
    error = None
    user = db.get_one_by_property('user', 'username', username)
    if not user:
        flash('User not found.')
        return redirect(url_for('show_teams'))
    teams = db.get_all_by_property('team', 'user', user['id'])

    return render_template('profile.html', error=error, teams=teams, username=username)

# Get or delete a team specified by the ID
@app.route('/team/<team_id>', methods=['GET', 'POST'])
def delete_team(team_id):
    error = None
    if request.method == 'POST':
        try:
            db.delete_one_by_id('team', team_id)
            flash('Successfully deleted team')
            return redirect(url_for('profile', username=session['username']))
        except db.OperationException as e:
            flash(e.message)

    return redirect(url_for('profile', username=session['username']))
