import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
CORS(app)

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
    return jsonify([dict(user) for user in users])

@app.route("/access", methods=["GET"])
def get_access():
    conn = db_user()
    access = conn.execute('SELECT * FROM access_rights').fetchall()
    conn.close()
    return jsonify([dict(item) for item in access])

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data["name"]
    role = data["role"]
    
    conn = db_user()
    conn.execute('INSERT INTO users (name, role) VALUES (?, ?)', (name, role))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/delete_user/<string:user_name>", methods=["DELETE"])
def delete_user(user_name):
    try:
        conn = db_user()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE name = ?', (user_name,))
        conn.commit()
        if cursor.rowcount > 0: # Vérifie si l'user à été delete
            return jsonify({"success": True, "message": "Utilisateur supprimé avec succès!"}), 200
        else:
            return jsonify({"success": False, "message": "Utilisateur non trouvé"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)