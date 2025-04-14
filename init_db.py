import sqlite3

# Connect to the database (creates database.db if it doesn't exist)
conn = sqlite3.connect('database.db')

# Open and run your SQL commands from schema.sql
with open('schema.sql') as f:
    conn.executescript(f.read())

# Save changes
conn.commit()

# Close connection
conn.close()

print("Database initialized successfully!")