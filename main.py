import os
from olama import send_answer
from user import User
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import bcrypt
from google.cloud import firestore
from GETDATA import get_data, get_infcoin_price
from trading_engine import execute_order


app = Flask(__name__)
app.secret_key = 'qwerty'  # Необходимо для работы сессий


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile_page():
    if 'user_id' not in session:
        return redirect(url_for('auth_page'))

    # Получаем пользователя из базы данных по ID из сессии
    user_id = session['user_id']
    user = User.collection.get(user_id)  # Предполагается, что метод get() принимает ID

    if not user:
        return redirect(url_for('auth_page'))

    return render_template('profilePage.html', username=user.name, phone=user.phone, user=user)
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем пользователя из сессии
    return redirect(url_for('index'))

@app.route('/authPage')
def auth_page():
    if 'user_id' in session:
        return redirect(url_for('main_page'))
    return render_template('authPage.html')

@app.post("/get_user")
def get_user():
    phone = request.form.get('phone')
    password = request.form.get('password')
    user_query = User.collection.filter('phone', '==', phone).get()

    if not user_query:  # Если список пуст
        return redirect(url_for('auth_page'))

    user = user_query  # Берем первого пользователя из списка
    if bcrypt.checkpw(password.encode(), user.password.encode()):
        session['user_id'] = user.id
        return redirect(url_for('main_page'))
    else:
        return redirect(url_for('auth_page'))

@app.route('/regPage')
def reg_page():
    if 'user_id' in session:
        return redirect(url_for('main_page'))
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

@app.route('/mainPage')
def main_page():
    if 'user_id' not in session:
        return redirect(url_for('auth_page'))

    # Получаем пользователя из базы данных по ID из сессии
    user_id = session['user_id']
    user = User.collection.get(user_id)  # Предполагается, что метод get() принимает ID

    if not user:
        return redirect(url_for('auth_page'))

    return render_template('mainPage.html', username=user.name, inf=get_infcoin_price(), bills="""""")

@app.post("/create_frame")
def create_frame():
    name = request.form.get('name')
    if not name:
        return "Error: No name provided", 400
    try:
        price, invest_up, logo = get_data(name)
        return render_template('activeframe.html',
                               name=name,
                               price=price,
                               invest_up=invest_up,
                               logo=logo)
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return "Error fetching data", 500


@app.post("/api/order")
def api_create_order():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Требуется авторизация"}), 401

    try:
        user = User.collection.get(session['user_id'])
        if not user:
            return jsonify({"success": False, "error": "Пользователь не найден"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Неверный формат запроса"}), 400

        required_fields = ['ticker', 'operation', 'lots']
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": "Не хватает обязательных полей"}), 400

        success, message = execute_order(
            user=user,
            ticker=data['ticker'],
            operation=data['operation'],
            lots=int(data['lots'])
        )

        return jsonify({
            "success": success,
            "message": message,
            "new_balance": user.balance_rub,
            "portfolio": user.portfolio
        })

    except Exception as e:
        error_msg = f"Ошибка обработки ордера: {str(e)}"
        print(error_msg)
        return jsonify({"success": False, "error": error_msg}), 500


@app.get("/get_valut_data/<ticker>")
def get_valut_data(ticker):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Получаем данные пользователя
        user = User.collection.get(session['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        price, invest_up, logo = get_data(ticker)
        # Формируем ответ
        return jsonify({
            "name": ticker,
            "icon": logo,
            "change_percent": invest_up,  # Можно реализовать получение изменения цены
            "price": f"{price} ₽ за 1 лот",
            "balance": user.portfolio.get(ticker, 0),
            "rubbles": user.balance_rub
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/send_message")
def api_send_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Неверный формат запроса"}), 400

        required_fields = ['message']
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": "Не хватает обязательных полей"}), 400
        print(data['message'])
        success, message = send_answer(data['message'])

        return jsonify({
            "success": success,
            "message": message
        })

    except Exception as e:
        error_msg = f"Ошибка обработки ордера: {str(e)}"
        print(error_msg)
        return jsonify({"success": False, "error": error_msg}), 500


if __name__ == '__main__':
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/infproject-t-firebase-adminsdk-fbsvc-59f397aa40.json"
        # Проверка подключения
        test_conn = firestore.Client()
        print("Firebase успешно подключен!")
    except Exception as e:
        print("Ошибка подключения к Firebase:", str(e))
        exit(1)
    app.run(port=8080, host='0.0.0.0')