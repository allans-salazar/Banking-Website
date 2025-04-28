from flask import Flask, request, jsonify
from flask import send_from_directory
import cx_Oracle

app = Flask(__name__)

# Database connection setup
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCLCDB")
connection = cx_Oracle.connect(user="system", password="oracle", dsn=dsn)

# Home route
@app.route('/')
def home():
    return '''
        <h1>CSCI Database Group Project</h1>
        <p>Backend Flask Server is running and connected to Oracle SQL</p>
        <p>Use the <strong>frontend website</strong> to search for users.</p>
    '''

@app.route('/frontend') #This is the frontend of the website http://127.0.0.1:5000/frontend
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

# API route to search for users
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