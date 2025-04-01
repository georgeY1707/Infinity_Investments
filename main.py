from user import User
from flask import Flask, render_template, redirect, url_for, request, session
import fireo
import bcrypt

app = Flask(__name__)
app.secret_key = 'qwerty'  # Необходимо для работы сессий

# Подключение к Firebase (добавьте ваш путь к сервисному аккаунту)
fireo.connection(connection="config/infproject-t-firebase-adminsdk-fbsvc-59f397aa40.json")


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
    # Получаем данные из формы
    name = request.form.get('name')
    lst_name = request.form.get('lst_name')
    password = request.form.get('password')
    phone = request.form.get('phone')

    # Хешируем пароль перед сохранением
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Создаем и сохраняем пользователя
    user = User(
        name=name,
        lst_name=lst_name,
        password=hashed_password,  # Сохраняем хеш пароля
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
    user.save()

    # Сохраняем ID пользователя в сессии
    session['user_id'] = user.id

    # Перенаправляем на главную страницу
    return redirect(url_for('main_page'))


@app.post("/get_user")
def get_user():
    # Получаем данные из формы входа
    phone = request.form.get('phone')
    password = request.form.get('password')

    # Ищем пользователя по телефону
    users = User.collection.filter('phone', '==', phone).fetch()
    if not users:
        return redirect(url_for('auth_page'))  # Пользователь не найден

    user = next(users)

    # Проверяем пароль
    if bcrypt.checkpw(password.encode(), user.password.encode()):
        session['user_id'] = user.id  # Сохраняем в сессии
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
    app.run(port=8080, host='0.0.0.0')