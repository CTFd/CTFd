from flask import Flask, render_template
import logging

# Инициализация flask-приложения
app = Flask(__name__)

# Функционал логирования
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
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

    logging.info('Homepage accessed')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

