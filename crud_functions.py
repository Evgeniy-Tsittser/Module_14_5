import sqlite3


def initiate_db():
    connection = sqlite3.connect('products.db')
    conn_user = sqlite3.connect('users_database.db')
    cursor = connection.cursor()
    cursor_2 = conn_user.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL
    );
    ''')

    cursor_2.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance INTEGER NOT NULL
    );
    ''')

def get_all_products():
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    products_list = cursor.execute("SELECT * FROM Products").fetchall()
    connection.commit()
    connection.close()
    return products_list

def add_user(username, email, age):
    conn_user = sqlite3.connect('users_database.db')
    cursor_2 = conn_user.cursor()
    cursor_2.execute(f'''
            INSERT INTO Users (username, email, age, balance)
            VALUES (?,?,?,?)
            ''', ((username, email, age, 1000)))
    conn_user.commit()
    conn_user.close()

def is_included(username):
    conn_user = sqlite3.connect('users_database.db')
    cursor_2 = conn_user.cursor()
    cursor_2.execute("SELECT * FROM Users WHERE username = ?", (username,))
    result = cursor_2.fetchone()
    conn_user.close()
    return result is not None





