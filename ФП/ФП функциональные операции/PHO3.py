orders = [
    {"order_id": 1, "customer_id": 101, "amount": 150.0},
    {"order_id": 2, "customer_id": 102, "amount": 200.0},
    {"order_id": 3, "customer_id": 101, "amount": 75.0},
    {"order_id": 4, "customer_id": 103, "amount": 100.0},
    {"order_id": 5, "customer_id": 101, "amount": 50.0},
    {"order_id": 6, "customer_id": 102, "amount": 300.0},
    {"order_id": 7, "customer_id": 103, "amount": 150.0},
    {"order_id": 8, "customer_id": 101, "amount": 80.0},
    {"order_id": 9, "customer_id": 102, "amount": 120.0},
    {"order_id": 10, "customer_id": 101, "amount": 60.0},
    {"order_id": 11, "customer_id": 104, "amount": 90.0},
    {"order_id": 12, "customer_id": 104, "amount": 100.0},
    {"order_id": 13, "customer_id": 103, "amount": 50.0},
    {"order_id": 14, "customer_id": 102, "amount": 70.0},
    {"order_id": 15, "customer_id": 104, "amount": 150.0},
    {"order_id": 16, "customer_id": 101, "amount": 200.0},
    {"order_id": 17, "customer_id": 103, "amount": 120.0},
    {"order_id": 18, "customer_id": 101, "amount": 180.0},
    {"order_id": 19, "customer_id": 102, "amount": 140.0},
    {"order_id": 20, "customer_id": 104, "amount": 90.0},
]

# Фильтрация заказов для определенного клиента
def filter_orders_by_customer(orders, customer_id):
    filtered_order_ids = [order["order_id"] for order in orders if order["customer_id"] == customer_id]
    return filtered_order_ids



# Подсчет общей суммы заказов для данного клиента
def calculate_total_order_amount(orders, customer_id):
    total_amount = sum(order["amount"] for order in orders if order["customer_id"] == customer_id)
    return total_amount

# Подсчет средней стоимости заказов для данного клиента
def calculate_average_order_cost(orders, customer_id):
    customer_orders = [order["amount"] for order in orders if order["customer_id"] == customer_id]
    if not customer_orders:
        return 0
    average_cost = sum(customer_orders) / len(customer_orders)
    return average_cost

# Пример использования функций
customer_id = 101
filtered_orders_ids = filter_orders_by_customer(orders, customer_id)
total_amount = calculate_total_order_amount(orders, customer_id)
average_cost = calculate_average_order_cost(orders, customer_id)

print(f"Заказы для клиента {customer_id}: {filtered_orders_ids}")
print(f"Общая сумма заказов для клиента {customer_id}: {total_amount}")
print(f"Средняя стоимость заказов для клиента {customer_id}: {average_cost}")
