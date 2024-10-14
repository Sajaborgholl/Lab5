#!/usr/bin/python
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

# Function to connect to the database
def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

# Function to create the users table
def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            country TEXT NOT NULL
        );
        ''')
        conn.commit()
        print("User table created successfully")
    except sqlite3.Error as e:
        print(f"User table creation failed: {e}")
    finally:
        conn.close()

# Function to insert a new user
def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
            (user['name'], user['email'], user['phone'], user['address'], user['country'])
        )
        conn.commit()  # Commit the transaction
        inserted_user = get_user_by_id(cur.lastrowid)  # Retrieve the newly inserted user by their ID
    except sqlite3.Error as e:
        conn.rollback()  # Roll back in case of an error
        print(f"Error inserting user: {e}")
    finally:
        conn.close()  # Ensure the connection is always closed
    return inserted_user

# Function to get all users
def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()

        # Convert each row to a dictionary and append it to the users list
        for i in rows:
            user = {
                "user_id": i["user_id"],
                "name": i["name"],
                "email": i["email"],
                "phone": i["phone"],
                "address": i["address"],
                "country": i["country"]
            }
            users.append(user)
    except sqlite3.Error as e:
        print(f"Error fetching users: {e}")
        users = []  # Return an empty list if an error occurs
    finally:
        conn.close()  # Ensure the connection is closed

    return users

# Function to get a user by their ID
def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        # Check if a user was found
        if row:
            user = {
                "user_id": row["user_id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "address": row["address"],
                "country": row["country"]
            }
        else:
            print(f"No user found with user_id: {user_id}")
    except sqlite3.Error as e:
        print(f"Error fetching user by ID: {e}")
        user = {}  # Return an empty dictionary if an error occurs
    finally:
        conn.close()  # Ensure the connection is closed

    return user

# Function to update a user
def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        # Execute the update query
        cur.execute(
            """
            UPDATE users
            SET name = ?, email = ?, phone = ?, address = ?, country = ?
            WHERE user_id = ?
            """,
            (user["name"], user["email"], user["phone"], user["address"], user["country"], user["user_id"])
        )
        conn.commit()  # Save the changes

        # Return the updated user details
        updated_user = get_user_by_id(user["user_id"])

    except sqlite3.Error as e:
        conn.rollback()  # Roll back any changes if an error occurs
        print(f"Error updating user: {e}")
        updated_user = {}  # Return an empty dictionary if the update fails

    finally:
        conn.close()  # Ensure the connection is always closed

    return updated_user

# Function to delete a user
def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        # Execute the delete query
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()  # Save the changes

        if cur.rowcount == 0:
            message["status"] = "User not found"
        else:
            message["status"] = "User deleted successfully"
    
    except sqlite3.Error as e:
        conn.rollback()  # Rollback in case of an error
        print(f"Error deleting user: {e}")
        message["status"] = "Cannot delete user"
    
    finally:
        conn.close()  # Ensure the connection is always closed

    return message


# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# API Endpoints
@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users()), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    user = request.get_json()
    required_fields = ["name", "email", "phone", "address", "country"]
    if not all(field in user for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400
    return jsonify(insert_user(user)), 201

@app.route('/api/users/update', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user)), 200

@app.route('/api/users/delete/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id)), 200

# Ensure the database is created on app startup
if __name__ == "__main__":
    create_db_table()  # Create table if it doesn't exist
    app.run(debug=True)  # Run the app in debug mode for development
