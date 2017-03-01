from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from dotateams import app

import db

#########################################
# API FOR OPERATIONS INVOLVING USER DATA
#########################################

# Log a user in given their username and password
@app.route('/api/user/login', methods=['GET', 'POST'])
def user_login():
    error = None
    request_body = request.get_json(force=True)
    username = request_body['username']
    password = request_body['password']
        
    user = db.get_one_by_property('user', 'username', username)
    if user:
        if check_password_hash(user['password'], password):
            print 'HERE!!!'
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user['id']

            return jsonify({}), 200
        else:
            jsonify({"error": 'Incorrect password.'}), 401
    else:
        jsonify({"error": 'The given username does not exist.'}), 404

    return jsonify({"error": request_body}), 500