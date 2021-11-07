"""
Simple "Hello, World" application using Flask
"""

import sqlite3
from flask import Flask, render_template, request, abort, g
from mbta_helper import find_stop_near

app = Flask(__name__)

DATABASE = 'webapp.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            "create table if not exists mbta(address text, vehicle text, name text, wheelchair integer)"
        )
        db.commit()


@app.route('/')
def hello():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def search_failed(e):
    return render_template('500.html'), 500


@app.route('/nearest_mbta', methods=['GET', 'POST'])
def nearest_mbta():
    if request.method == 'POST':
        form = request.form
        address = form['address']
        vehicles = list()
        for key in form.keys():
            if key != 'address':
                vehicles.append(key)
        vehicle_types = ','.join(vehicles)
        db = get_db()
        cur = db.cursor()
        cur.execute('select * from mbta where address = ? and vehicle = ?',
                    [address, vehicle_types])
        result = cur.fetchone()
        cur.close()
        if not result:
            try:
                name, wheelchair_accessibility = find_stop_near(
                    address, vehicle_types)
            except IndexError:
                abort(500)
            cur = get_db().cursor()
            cur.execute(
                'insert into mbta (address, vehicle, name, wheelchair) values (?, ?, ?, ?)',
                (address, vehicle_types, name, wheelchair_accessibility))
            cur.close()
            db.commit()
        else:
            name = result[2]
            wheelchair_accessibility = result[3] == 1
    return render_template('mbta_station.html',
                           name=name,
                           wheelchair_accessibility=wheelchair_accessibility)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)