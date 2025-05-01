from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cx_Oracle
import os

# === Setup paths for frontend/static and frontend/index.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.abspath(os.path.join(base_dir, '..', 'frontend'))
static_dir = os.path.join(template_dir, 'static')

# === Create Flask app with static/template folders ===
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
CORS(app)

# === Serve index.html ===
@app.route('/')
def serve_index():
    return send_from_directory(template_dir, 'index.html')

# === Oracle DB connection ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCLCDB")
connection = cx_Oracle.connect(user="system", password="oracle", dsn=dsn)

# === API: Login route ===
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"})

    cursor = connection.cursor()
    cursor.execute("""
        SELECT username, role FROM users 
        WHERE username = :1 AND password = :2
    """, (username, password))
    
    user = cursor.fetchone()

    if user:
        return jsonify({"username": user[0], "role": user[1]})
    else:
        return jsonify({"error": "Invalid credentials"})

# === Optional: Static file serving (script.js, etc.) ===
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_dir, filename)

# === Start the Flask server ===
if __name__ == '__main__':
    app.run(debug=True)