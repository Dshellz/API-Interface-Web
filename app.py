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

def init_db():
    conn = db_user()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        badgeuid TEXT)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS rooms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
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



# Ajout utilisateurs et Modifications

@app.route("/users", methods=["GET"])
def get_users():
    conn = db_user()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

# Verification BadgeUID

@app.route("/check_badge", methods=["POST"])
def check_badge():
    data = request.get_json()
    
    if not data or "badgeuid" not in data:
        return jsonify({"error": "badgeuid requis"}), 400

    badgeuid = data["badgeuid"]

    conn = db_user()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE badgeuid = ?", (badgeuid,))
    user = cursor.fetchone()
    conn.close()

    if user and badgeuid == "c31f1911":
        return "access_ok", 200
    else:
        return "access_denied", 403
    
@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data["name"]
    role = data["role"]
    badgeuid = data.get("badgeuid", None)
    
    conn = db_user()
    conn.execute('INSERT INTO users (name, role, badgeuid) VALUES (?, ?, ?)', (name, role, badgeuid))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "L'utilisateur a été ajouté !"})

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

# Ajout de salle & Horaires

@app.route("/rooms", methods=["GET"]) # Récuperer les salles
def get_rooms():
    conn = db_user()
    rooms = conn.execute('SELECT * FROM rooms').fetchall()
    conn.close()
    
    if rooms:
        return jsonify([dict(room) for room in rooms])
    else:
        return jsonify({"success": False, "message": "Aucune salle disponible"}), 404

@app.route("/add_room", methods=["POST"])  # Ajouter une salle avec horaires
def add_room():
    data = request.get_json()
    room_name = data["room_name"]
    start_time = data["start_time"]
    end_time = data["end_time"]
    
    # Insérer la salle dans la table rooms et récupere l'ID
    conn = db_user()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO rooms (room_name) VALUES (?)', (room_name,))
    conn.commit()
    room_id = cursor.lastrowid  # Récupère l'ID de la salle
    
    conn.execute('INSERT INTO acces_horaire (room_id, start_time, end_time) VALUES (?, ?, ?)', 
                 (room_id, start_time, end_time))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Salle ajouté avec succès !"})

@app.route("/set_horaire", methods=["POST"])
def set_horaire():
    data = request.get_json()
    room_id = data["room_id"]
    start_time = data["start_time"]
    end_time = data["end_time"]
    
    conn = db_user()
    conn.execute('''
        INSERT OR REPLACE INTO acces_horaire (room_id, start_time, end_time)
        VALUES (?, ?, ?)
    ''', (room_id, start_time, end_time))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/get_horaire", methods=["GET"])
def get_horaire():
    room_id = request.args.get("room_id")
    conn = db_user()
    horaire = conn.execute('''
        SELECT acces_horaire.id, acces_horaire.room_id, acces_horaire.start_time, acces_horaire.end_time, rooms.room_name
        FROM acces_horaire
        JOIN rooms ON acces_horaire.room_id = rooms.id
        WHERE acces_horaire.room_id = ?
    ''', (room_id,)).fetchone()
    conn.close()

    if horaire:
        return jsonify({
            "room_id": horaire["room_id"],
            "room_name": horaire["room_name"],
            "start_time": horaire["start_time"],
            "end_time": horaire["end_time"]
        })
    else:
        return jsonify({"success": False, "message": "Horaire non trouvé"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)