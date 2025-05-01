from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cx_Oracle
import os

# Set correct paths
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.abspath(os.path.join(base_dir, '..', 'frontend'))
static_dir = os.path.join(template_dir, 'static')

# Create Flask app
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
CORS(app)

# Serve index.html from frontend
@app.route('/')
def serve_index():
    return send_from_directory(template_dir, 'index.html')

# Oracle DB connection (adjust if needed)
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCLCDB")
connection = cx_Oracle.connect(user="system", password="oracle", dsn=dsn)

# API route to get user info
@app.route('/get_user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    cursor = connection.cursor()
    cursor.execute("SELECT username, role FROM users WHERE user_id = :1", (user_id,))
    user = cursor.fetchone()
    if user:
        return jsonify({"username": user[0], "role": user[1]})
    else:
        return jsonify({"error": "User not found"})

if __name__ == '__main__':
    app.run(debug=True)