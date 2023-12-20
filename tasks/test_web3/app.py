from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

DATABASE = 'data/database.db'

def create_database():
    """
    Создаёт базу данных (users) для таска с проставленными полями: username, password, role

    Args:
        none
    
    Returns:
        none
    
    Raises:
        none
    """
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin_password', 'admin'))
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('user', 'user_password', 'user'))
    
    conn.commit()
    conn.close()

create_database()

@app.route('/')
def login():
    """
    Служебная функция модуля Flask,
    декоратором обозначивается путь веб-приложения,
    а функция задаёт дейтствия при переходе по данному пути

    Args:
        none

    Returns:
        render_template, рендерит заданную HTML-страницу на клиенте (в браузере конечного пользователя)

    Raises: Код состояния HTTP, в зависимости от взаимодействия:
        200, если статус - ОК
        404, если пользователь обратился по несуществующему пути или обратился к несуществующему ресурсу (Not found)
        5XX, если произошла серверная ошибка
    """
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def check_login():
    """
    Проверка введённых пользователем данных для авторизации

    Args:
        none

    Returns:
        str: значение флага в случае успешной авторизации
        str: сообщение о проваленной попытке логина

    Raises:
        none
    """
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
    user = cursor.fetchone()
    conn.close()

    if user is not None and user[3] == 'admin':
        return f"Flag: {os.getenv('WEB3_FLAG')}"
    else:
        return "Login failed. Try again."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

