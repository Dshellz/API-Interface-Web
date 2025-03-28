import sqlite3
from flask import Flask, render_template, request 

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')  # Charge la page HTML


def db_user():
    conn = sqlite3.connect('db_dash.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db(): # Créer les tables si elles n'existent pas encore
    conn = db_user()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS rooms (
                        id INTEGER PRIMARY KEY,
                        room_name TEXT NOT NULL)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS acces_horaire (
                        id INTEGER PRIMARY KEY,
                        room_id INTEGER NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        FOREIGN KEY (room_id) REFERENCES rooms(id))''')
    conn.commit()
    conn.close()

init_db()

@app.route("/users", methods=["GET"])
def get_users():
    conn = db_user()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return ([dict(user) for user in users])

@app.route("/access", methods=["GET"])
def get_access():
    conn = db_user()
    access = conn.execute('SELECT * FROM access_rights').fetchall()
    conn.close()
    return ([dict(item) for item in access])

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data["name"]
    role = data["role"]
    
    conn = db_user()
    conn.execute('INSERT INTO users (name, role) VALUES (?, ?)', (name, role))
    conn.commit()
    conn.close()

    return ({"success": True})

@app.route("/delete_user/<string:user_name>", methods=["DELETE"])
def delete_user(user_name):
    conn = db_user()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE name = ?', (user_name,)) # Sup un user
    conn.commit()
    
    if cursor.rowcount > 0: # Verif si un utilisateur a été supprimé
        conn.close()
        return ({"success": True})
    else:
        conn.close()
        return ({"success": False, "message": "Utilisateur non trouvé"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)