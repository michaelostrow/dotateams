from dotateams import app

import sqlite3
from flask import g

############################
# DATABASE MODULE
############################

# Custon exception to handle from this class
class OperationException(Exception):
    pass

# Opens a new database connection if there is none yet
# for the current application context.
def get_db():
    print app.config
    if not hasattr(g, 'sqlite_db'):
        rv = sqlite3.connect(app.config['DATABASE'])
        rv.row_factory = sqlite3.Row
        g.sqlite_db = rv
    return g.sqlite_db

# Closes the database again at the end of the request.
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Works as a command to initializes the database.
@app.cli.command('initdb')
def initdb_command():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print('Initialized the database.')

# Gets one item from a table by where prop matches value
def get_one_by_property(table, prop, value):
    db = get_db()
    query = 'select * from {0} where {1} = ?'.format(table, prop)
    return db.execute(query, [value]).fetchone()

# Gets all items from a table by where prop matches value
def get_all_by_property(table, prop, value):
    db = get_db()
    query = 'select * from {0} where {1} = ?'.format(table, prop)
    return db.execute(query, [value]).fetchall()

# Gets all items from a table, sorts in order given by sort_order
# on the given column
def get_all_items(table, column, sort_order):
    db = get_db()
    query = 'select * from {0} order by {1} {2}'.format(table, column, sort_order)
    return db.execute(query).fetchall()

# Gets all teams as well as the username of that teams creator
def get_all_teams_with_creators_username():
    db = get_db()
    return db.execute('select team.*, user.username from team inner join user where user.id = team.user order by created_at desc')

# Creates a new entry in table giving the given values the 
# given props, returns the ID of the created item
def create_new_entry(table, props, values):
    props = ','.join(props)

    if table == 'user':
        query = 'insert into {0} ({1}) values (?,?)'.format(table, props)
    else:
        query = 'insert into {0} ({1}) values (?,?,?)'.format(table, props)
    db = get_db()
    cursor = db.execute(query, values)
    db.commit()
    return cursor.lastrowid

# Creates a new user with the given username and hashed_pw
def create_new_user(username, hashed_pw):
    try:
        return create_new_entry('user', ['username', 'password'], [username, hashed_pw])
    except sqlite3.IntegrityError:
        raise OperationException('The username you have chosen is already in use.')
    except Exception as e:
        print e
        raise OperationException('Unexpected error in signup, please try again.')

# Creates a new team with all the given team properties
def create_new_team(user, title, description):
    try:
        return create_new_entry('team', ['user', 'title', 'description'], [user, title, description])
    except sqlite3.IntegrityError:
        raise OperationException('The team title you have chosen is already in use.')
    except Exception:
        raise OperationException('Unexpected error in team creation, please try again.')

# Deletes a resource from the given table with the given ID
def delete_one_by_id(table, id):
    query = 'delete from {0} where id=?'.format(table)

    try:
        db = get_db()
        cursor = db.execute(query, [id])
        db.commit()
        return True
    except Exception as e:
        print e
        raise OperationException('Error when deleting this team, please try again')
