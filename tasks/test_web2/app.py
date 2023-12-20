from flask import Flask, request, render_template_string, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler

# Инициализация веб-приложения
app = Flask(__name__)

# Logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

@app.route('/') # путь
def home():
    """
    Домашняя страница приложения (корень приложения, /)

    Args:
        none

    Returns:
        Object: built-in render_template_string (Flask), отрисовывает страницу на клиенте, в данном случае, не в виде html-файда, как метод render_template,
        а в виде поданной в качестве аргумента последовательности символов, представляющих из себя валидный HTML-документ или набор тегов.

    Raises:
        200, 4XX, 5XX коды состояния HTTP.
    """


    app.logger.info("Home page accessed")
    return render_template_string('''
        <h1>Welcome to the Vulnerable App</h1>
        <p>Use /ping?ip= to check IP availability</p>
    ''')

@app.route('/ping', methods=['GET']) # путь, массив из списка принимаемых HTTP-методов: GET, POST, PUT, и т.д.
def ping():
    """
    Функция, осуществляющая работу UNIX-команды "ping" и вывод её результата в шаблон страницы пользователю по запросу.
    Функция намеренно подвержена уязвимости вида OS Command Injection в рамках тестовой среды.

    Args:
        none

    Returns:
        bytearray -> str: результат работы команды ping.

    Raises: 200 - OK, 4XX - client-side error, 5XX - server-side error
    """
    ip = request.args.get('ip', '')
    if not ip:
        return "No IP address provided.", 400

    cmd = f"ping -c 1 {ip}"
    result = os.popen(cmd).read()

    app.logger.info(f"Ping command executed: {cmd}")

    return render_template_string('''
        <h1>Check IP Availability</h1>
        <form method="get">
            <label>Enter IP address:</label>
            <input type="text" name="ip">
            <input type="submit" value="Ping">
        </form>
        <pre>{{ result }}</pre>
    ''', result=result)

# Кастомные обработчики ошибок
@app.errorhandler(404)
def page_not_found(e):
    """
    Обработчик ошибки для кода 404 - обращение к несуществующему ресурсу.

    Args:
        e (object): Объект исключения, вызывающий ошибку Not Found и логирующий её соответсвующим образом.
    
    Returns:
        json: словарь с описанием ошибки, её кодом, и наборов других HTTP-хедеров, которые возвращаются пользователю на его request.
    
    Raises:
        HTTP 404 Not Found.
    """
    app.logger.error("Page not found: %s", (request.path))
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_server_error(e):
    """
    Обработчик ошибки для кода 500 - внутренняя ошибка сервера.

    Args:
        e (object): Объект исключения, вызывающий ошибку Internal Server Error и логирующий её соответсвующим образом.
    
    Returns:
        json: словарь с описанием ошибки, её кодом, и наборов других HTTP-хедеров, которые возвращаются пользователю на его request.
    
    Raises:
        HTTP 500 Internal Server Error.
    """
    app.logger.error("Server error: %s", (str(e)))
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
