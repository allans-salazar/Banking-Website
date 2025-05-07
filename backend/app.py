from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cx_Oracle
import os

'''
Here are the explanations for the libraries used in this code:

- Flask is a micro web framework for Python. It is lightweight and easy to use, making it a popular choice for building web applications. 
Using request, jsonify, send_from_directory, and CORS from flask to handle requests. 

    request:
        •	Used to handle incoming HTTP requests, especially to access POST data from forms or JSON.
        •	Example: request.get_json()

    jsonify:
        •	Converts Python dictionaries or lists into JSON-formatted HTTP responses.
        •	Useful for APIs and client-server communication.

    send_from_directory:
        •	Lets you serve static files (e.g. HTML, CSS, JS) from a folder like your frontend/.
        •	Example: send_from_directory(app.static_folder, "index.html")

    CORS (Cross-Origin Resource Sharing):
        •	Enables requests from different origins (like accessing Flask from localhost:5000 while your HTML is hosted at another port or location).
        •	Prevents browser security errors when making frontend-to-backend API calls.

    
- cx_Oracle is Oracle’s official Python library for connecting to Oracle databases. Used to create database connections, run queries, and handle results.

- os gives access to operating system-level functions like file paths, environment variables, and directory access.
'''

# === Setup paths for frontend/static and frontend/index.html ===
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.abspath(os.path.join(base_dir, '..', 'frontend'))
static_dir = os.path.join(template_dir, 'static')

# === Create Flask app with static/template folders ===
app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

'''
The word "Serve" is how the Python backend delivers static pages like HTML, CSS, or JavaScript.
So when inserting these codes the Flask listens for a request to /file.html (usually from typing it in the browser or clicking a link).
Then it responds by sending the sign_up.html file from your template_dir.
'''

# === Serve index.html ===
@app.route('/')
def serve_index():
    return send_from_directory(template_dir, 'index.html')

# === Oracle DB connection ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="ORCLCDB")
connection = cx_Oracle.connect(user="system", password="oracle", dsn=dsn)

def get_db_connection():
    return cx_Oracle.connect(user="system", password="oracle", dsn="localhost:1521/ORCLCDB")


''' 
API: Login route for users and admins --
This route handles user login and checks for failed login attempts. If a user has 5 or more failed login attempts, they are blocked
This is enabled when the function "login_user" is called from the frontend in index.html. 
'''

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for failed login attempts
        cursor.execute("""
            SELECT COUNT(*) FROM logs
            WHERE user_id = (SELECT user_id FROM users WHERE username = :1)
            AND log_type = 'failed_login'
        """, (username,))
        failed_count = cursor.fetchone()[0]

        # If user has 5 or more failed login attempts, block them
        if failed_count >= 5:
            cursor.execute("""
                INSERT INTO logs (user_id, log_type)
                VALUES ((SELECT user_id FROM users WHERE username = :1), 'blocked_user')
            """, (username,))
            conn.commit()
            return jsonify({"error": "You have been blocked due to too many failed login attempts."}), 403

        # Validation of credentials
        cursor.execute("""
            SELECT user_id, role FROM users
            WHERE username = :1 AND password = :2
        """, (username, password))
        row = cursor.fetchone()

        # If credentials are valid, fetch user role and name
        if row:
            user_id, role = row
            cursor.execute("SELECT name FROM customers WHERE user_id = :1", (user_id,))
            name_row = cursor.fetchone()
            name = name_row[0] if name_row else "Admin"
            return jsonify({"message": role, "name": name})
        else:
            # Else, login failed... inserting a login attempt in Logs table
            cursor.execute("""
                INSERT INTO logs (user_id, log_type)
                VALUES ((SELECT user_id FROM users WHERE username = :1), 'failed_login')
            """, (username,))
            conn.commit()
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# === Serve sign_up.html ===
@app.route('/sign_up.html')
def serve_sign_up():
    return send_from_directory(template_dir, 'sign_up.html')

# === Serve user_page.html ===
@app.route('/user_page.html')
def serve_user_page():
    return send_from_directory(template_dir, 'user_page.html')


'''
This route in Flask is used to record suspicious activity, like:
	•	Failed login attempts
	•	SQL injection attempts
	•	Incorrect admin PINs

This route is called when the function "log_suspicious" is called from the frontend in index.html.
'''
@app.route('/log_suspicious', methods=['POST'])
def log_suspicious():
    data = request.get_json()
    username = data.get("username")
    log_type = data.get("log_type", "suspicious_input")

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        #Find user_id by username
        cursor.execute("SELECT user_id FROM users WHERE username = :1", (username,))
        result = cursor.fetchone()
        user_id = result[0] if result else None

        # If user_id is not found, return an error
        cursor.execute("INSERT INTO logs (user_id, log_type) VALUES (:1, :2)", (user_id, log_type))
        connection.commit()
        return jsonify({'message': 'Log recorded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

'''
This Flask route handles user registration by:
	•	Receiving new user data from the frontend
	•	Inserting that data into the users and customers tables in your Oracle database

sign_up.html is connected to a function in script.js the function is called "registerUser".
'''
@app.route('/register', methods=['POST'])
def register():
    # Get data from the request (frontend)
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    ssn = data['ssn']
    name = data['name']
    last_name = data['last_name']

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert the data into users table
        user_id_var = cursor.var(cx_Oracle.NUMBER)
        cursor.execute("""
            INSERT INTO users (username, password, name, last_name, email, ssn)
            VALUES (:1, :2, :3, :4, :5, :6)
            RETURNING user_id INTO :7
        """, (username, password, name, last_name, email, ssn, user_id_var))

        user_id = int(user_id_var.getvalue()[0])

        # Insert into customers table
        cursor.execute("""
            INSERT INTO customers (user_id, name, last_name)
            VALUES (:1, :2, :3)
        """, (user_id, name, last_name))

        connection.commit()
        return jsonify({'message': 'User registered successfully'}), 200

    except cx_Oracle.DatabaseError as e:
        error_message = str(e)
        return jsonify({'error': f'Registration error: {error_message}'}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# === Serve admin_.html ===
@app.route("/admin_dashboard.html")
def serve_admin_dashboard():
    return send_from_directory(app.static_folder, "admin_dashboard.html")

'''
This route is used to fetch logs from the database for the admin dashboard:
    •   View failed login attempts
    •   View failed 2FA PIN attempts
    •   View SQL injection attempts

It retrieves the logs from the logs table and joins it with the users table to get the username.
This is called when the function "getLogs" is called from the frontend in admin_dashboard.html.
'''
@app.route("/admin/logs", methods=["GET"])
def get_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Query all logs with user information
        cursor.execute("""
            SELECT u.username, l.log_type, TO_CHAR(l.timestamp, 'YYYY-MM-DD HH24:MI:SS')
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.user_id
            ORDER BY l.timestamp DESC
        """)
        rows = cursor.fetchall()
        logs = [{"username": r[0], "log_type": r[1], "timestamp": r[2]} for r in rows]
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    
'''
This route is used to fetch user page:
    •   Fetches the user's name and balance from the customers table
    •   Fetches the user's transactions from the transactions table

This is called when the function "getDashboardData" is called from the frontend in user_page.html.
'''
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

        # Fetch Balance and Name from Customers Table
        cursor.execute("SELECT name, balance FROM customers WHERE user_id = :1", [user_id])
        customer = cursor.fetchone()

        if not customer:
            return jsonify({"error": "Customer record not found"}), 404

        name, balance = customer

        # Fetch transactions from Transactions Table
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
        #Format and send data to frontend
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