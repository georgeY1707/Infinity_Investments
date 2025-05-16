import json

from GETDATA import get_data


def get_infcoin_price():
    with open('config/infcoin-price-temp.json') as file:
        return json.load(file)['price']


def execute_order(user, ticker, operation, lots):
    """Исполнение ордера с улучшенной обработкой ошибок"""
    try:
        # Get data and unpack the tuple (we only need the price)
        price_data = get_data(ticker)
        if ticker == 'INFCOIN':
            price = get_infcoin_price()
        elif isinstance(price_data, tuple):
            price = price_data[0]  # Get the first element (price)
            # Convert price to float if it's a string
            if isinstance(price, str):
                price = float(price.replace(' ₽', '').replace(',', '.').strip())
        else:
            price = price_data  # In case it's not a tuple (like for infcoin)

        # 2. Проверяем баланс
        if operation == "Buy":
            total_cost = price * lots
            if user.balance_rub < total_cost:
                return False, f"Недостаточно средств. Нужно: {total_cost} ₽, доступно: {user.balance_rub} ₽"

            # Обновляем данные пользователя
            user.balance_rub -= total_cost
            user.portfolio[ticker] = user.portfolio.get(ticker, 0) + lots
        else:
            available_lots = user.portfolio.get(ticker, 0)
            if available_lots < lots:
                return False, f"Недостаточно лотов. Доступно: {available_lots}, запрошено: {lots}"

            user.portfolio[ticker] -= lots
            user.balance_rub += price * lots * 10

        # 3. Сохраняем изменения
        user.save()
        return True, f"Ордер исполнен. {'Куплено' if operation == 'Buy' else 'Продано'} {lots} лотов по {price} ₽"

    except Exception as e:
        error_msg = f"Ошибка исполнения ордера: {str(e)}"
        print(error_msg)
        return False, error_msg