import json
import math
from flask import Flask, redirect, url_for, render_template, request, session, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)
app.secret_key = 'rfgejgyso1XQ3*'  # Change to your secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATABASE = '../db/countries.db'

# User class
class User(UserMixin):
    def __init__(self, id, username, is_admin):
        self.id = id
        self.username = username
        self.is_admin = is_admin

# User Loader
@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
    if user:
        return User(str(user['id']), user['username'], user['is_admin'])
    return None

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        # Create continents table
        c.execute('''CREATE TABLE IF NOT EXISTS continents (
                     id INTEGER PRIMARY KEY,
                     name TEXT UNIQUE)''')
        # Create countries table
        c.execute('''CREATE TABLE IF NOT EXISTS countries (
                     id INTEGER PRIMARY KEY,
                     name TEXT,
                     continent_id INTEGER,
                     iso2 TEXT UNIQUE,
                     FOREIGN KEY(continent_id) REFERENCES continents(id))''')
        # Create visited_countries table
        c.execute('''CREATE TABLE IF NOT EXISTS visited_countries (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     country_id INTEGER UNIQUE,
                     user_id INTEGER,
                     FOREIGN KEY(country_id) REFERENCES countries(id),
                     FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password_hash TEXT NOT NULL,
                     is_admin BOOLEAN NOT NULL DEFAULT 0)''')

init_db()

@app.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = 'Guest'  # Or handle the case where the user is not logged in as you see fit
        
    return render_template('index.html', username=username)

@app.route('/continents', methods=['GET'])
def continents():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name FROM continents")
        continents = c.fetchall()
    return jsonify([{'id': continent[0], 'name': continent[1]} for continent in continents])

@app.route('/countries', methods=['GET'])
def countries():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row  # This enables column access by name
        c = conn.cursor()
        # Adjusted query to include a LEFT JOIN with visited_countries table and check for visited status
        c.execute('''
            SELECT countries.id, countries.name, continents.name as continent_name, 
            CASE WHEN visited_countries.country_id IS NOT NULL THEN TRUE ELSE FALSE END as visited
            FROM countries
            JOIN continents ON countries.continent_id = continents.id
            LEFT JOIN visited_countries ON countries.id = visited_countries.country_id AND visited_countries.user_id = ?
            ORDER BY continents.name, countries.name
        ''', (current_user.id,))
        rows = c.fetchall()
        
        # Organize countries by continent
        continents = {}
        for row in rows:
            continent_name = row['continent_name']
            if continent_name not in continents:
                continents[continent_name] = []
            continents[continent_name].append({
                "id": row['id'],
                "name": row['name'],
                "visited": row['visited']
            })

    # Convert the continents dictionary to a list of dictionaries for JSON serialization
    continents_list = [{"name": name, "countries": countries} for name, countries in continents.items()]
    return jsonify(continents_list)

@app.route('/visit', methods=['POST'])
def visit_country():
    print(current_user.id)
    try:
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            # Clear previous entries for this user
            c.execute("DELETE FROM visited_countries WHERE user_id = ?", (current_user.id,))
            
            country_ids = request.get_json().get('visitedCountries')
            if country_ids:
                # Prepare for inserting multiple records efficiently
                for country_id in country_ids:
                    c.execute("INSERT INTO visited_countries (country_id, user_id) VALUES (?, ?)", (country_id, current_user.id))
                    
            conn.commit()            
            return jsonify({"success": True, "message": f"{len(country_ids)} countries marked as visited."})
        #else:
        #    return jsonify({"success": False, "message": "No country IDs provided."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/visited', methods=['GET'])
def visited():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT c.id, c.name FROM countries c INNER JOIN visited_countries v ON c.id = v.country_id")
        countries = c.fetchall()
    return jsonify([{'id': country[0], 'name': country[1]} for country in countries])

@app.route('/visited_countries', methods=['GET'])
def visited_countries():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('''
            SELECT iso2 FROM countries
            JOIN visited_countries ON countries.id = visited_countries.country_id
            WHERE visited_countries.user_id = ?
        ''', (current_user.id,))
        visited = [dict(row) for row in c.fetchall()]
    return jsonify(visited)

@app.route('/countries_stats', methods=['GET'])
def countries_stats():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Total countries
        c.execute('SELECT COUNT(*) AS total FROM countries')
        total_countries = c.fetchone()['total']
        # Visited countries
        c.execute('SELECT COUNT(*) AS visited FROM visited_countries WHERE visited_countries.user_id = ?', (current_user.id,))
        visited_countries = c.fetchone()['visited']
        # Calculate percentage, rounded up
        percentage_visited = math.ceil((visited_countries / total_countries) * 100) if total_countries else 0
    return jsonify({"total": total_countries, "visited": visited_countries, "percentage": percentage_visited})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['is_admin'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            return 'Login failed'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return 'Unauthorized', 403

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        is_admin = request.form.get('is_admin') == 'on'
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                           (username, password, is_admin))
            conn.commit()
        return redirect(url_for('admin'))  # Redirect to clear POST data and refresh the page

    # Fetch all users to display
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, is_admin FROM users")
        users = cursor.fetchall()

    return render_template('admin.html', users=users)

@app.route('/admin/change_password', methods=['POST'])
@login_required
def change_password():
    if not current_user.is_admin:
        return 'Unauthorized', 403

    user_id = request.form['user_id']
    new_password = request.form['new_password']
    hashed_password = generate_password_hash(new_password)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()

    flash('Password updated successfully.', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
