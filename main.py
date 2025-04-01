import os

from user import User
from flask import Flask, render_template, redirect, url_for, request, session
import bcrypt
from fireo import connection
from google.cloud import firestore


app = Flask(__name__)
app.secret_key = 'qwerty'  # Необходимо для работы сессий

@app.route('/authPage')
def auth_page():
    return render_template('authPage.html')


@app.route('/mainPage')
def main_page():
    # Проверяем, что пользователь вошел (сессия существует)
    if 'user_id' not in session:
        return redirect(url_for('auth_page'))  # Перенаправляем на страницу входа
    return render_template('mainPage.html')


@app.route('/regPage')
def reg_page():
    return render_template('regPage.html')


@app.post("/create_user")
def create_user():
    try:
        # Получаем данные из формы
        name = request.form.get('name')
        password = request.form.get('password')
        phone = request.form.get('phone')

        # Проверка обязательных полей
        if not all([name, password, phone]):
            return redirect(url_for('reg_page'))

        # Проверяем, не существует ли уже пользователь с таким телефоном
        if User.collection.filter('phone', '==', phone).get():
            return redirect(url_for('reg_page'))

        # Хешируем пароль
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Создаем пользователя
        user = User(
            name=name,
            password=hashed_password,
            phone=phone,
            bills={
                'rubles': 0,
                'infcoin': 0,
                'YDEX': 0,
                'LKOH': 0,
                'SBER': 0,
                'T': 0,
                'NVTK': 0,
                'ROSN': 0
            }
        )

        # Сохраняем пользователя
        user.save()

        # Проверяем, что сохранение прошло успешно
        if not user.id:
            raise Exception("Не удалось сохранить пользователя")

        # Авторизуем пользователя
        session['user_id'] = user.id
        return redirect(url_for('main_page'))

    except Exception as e:
        print("Ошибка при создании пользователя:", str(e))
        return redirect(url_for('reg_page'))


@app.post("/get_user")
def get_user():
    # Получаем данные из формы входа
    phone = request.form.get('phone')
    password = request.form.get('password')

    # Ищем пользователя по телефону
    user_query = User.collection.filter('phone', '==', phone).get()

    if user_query is None:  # Если пользователь не найден
        return redirect(url_for('auth_page'))  # Перенаправляем на страницу входа

    # Проверяем пароль
    if bcrypt.checkpw(password.encode(), user_query.password.encode()):
        session['user_id'] = user_query.id  # Сохраняем в сессии
        return redirect(url_for('main_page'))
    else:
        return redirect(url_for('auth_page'))  # Неверный пароль


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем пользователя из сессии
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    try:
        #connection("config/infproject-t-firebase-adminsdk-fbsvc-59f397aa40.json")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"config\infproject-t-firebase-adminsdk-fbsvc-59f397aa40.json"
        # Проверка подключения
        test_conn = firestore.Client()
        print("Firebase успешно подключен!")
    except Exception as e:
        print("Ошибка подключения к Firebase:", str(e))
        exit(1)
    app.run(port=8080, host='0.0.0.0')