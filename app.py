from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_user', methods=['GET'])
def get_user():
    username = request.args.get('username')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    else:
        return jsonify({'error': 'User not found'})

if __name__ == '__main__':
    app.run(debug=True)