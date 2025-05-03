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

def get_db_connection():
    return cx_Oracle.connect(user="system", password="oracle", dsn="localhost:1521/ORCLCDB")

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
        SELECT name, role FROM users 
        WHERE username = :1 AND password = :2
    """, (username, password))

    user = cursor.fetchone()

    if user:
        return jsonify({
            "name": user[0],  # user[0] is the name
            "role": user[1], # user[1] is the role
            "username": username # Return the username for the frontend
        })
    else:
        return jsonify({"error": "Invalid credentials"})
    
@app.route('/sign_up.html')
def serve_sign_up():
    return send_from_directory(template_dir, 'sign_up.html')

@app.route('/user_page.html')
def serve_user_page():
    return send_from_directory(template_dir, 'user_page.html')

# === API: Register route ===
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get("name")
    lastname = data.get("lastname")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    ssn = data.get("ssn")

    # Basic validation
    if not all([name, lastname, username, email, password, ssn]):
        return jsonify({"error": "Missing required fields"})

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO users (name, last_name, username, email, password, ssn, role)
            VALUES (:1, :2, :3, :4, :5, :6, 'customer')
        """, (name, lastname, username, email, password, ssn))
        connection.commit()
        return jsonify({"message": "Account created successfully!"})
    except Exception as e:
        print("Registration error:", e)
        return jsonify({"error": "Registration failed."})
    
@app.route('/dashboard/<username>', methods=['GET'])
def get_dashboard_data(username):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Get user_id from username
        cursor.execute("SELECT user_id FROM users WHERE username = :1", [username])
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "User not found"}), 404

        user_id = result[0]

        # Fetch balance and name from customers
        cursor.execute("SELECT name, balance FROM customers WHERE user_id = :1", [user_id])
        customer = cursor.fetchone()

        if not customer:
            return jsonify({"error": "Customer record not found"}), 404

        name, balance = customer

        # Fetch transactions
        cursor.execute("""
            SELECT TO_CHAR(transaction_date, 'YYYY-MM-DD HH24:MI:SS'), transaction_type, amount 
            FROM transactions 
            WHERE user_id = :1 
            ORDER BY transaction_date DESC
        """, [user_id])
        transactions = cursor.fetchall()

        transaction_list = [
            {"date": row[0], "description": row[1], "amount": float(row[2])}
            for row in transactions
        ]

        return jsonify({
            "name": name,
            "balance": float(balance),
            "transactions": transaction_list
        })

    except cx_Oracle.DatabaseError as e:
        error_message = str(e)
        return jsonify({"error": f"Database error: {error_message}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# === Optional: Static file serving (script.js, etc.) ===
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_dir, filename)

# === Start the Flask server ===
if __name__ == '__main__':
    app.run(debug=True)