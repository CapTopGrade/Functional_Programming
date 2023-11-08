users = [
    {"name": "Alice", "expenses": [100, 50, 75, 200]},
    {"name": "Bob", "expenses": [50, 75, 80, 100]},
    {"name": "Charlie", "expenses": [200, 300, 50, 150]},
    {"name": "David", "expenses": [100, 200, 300, 400]},
    {"name": "Eve", "expenses": [150, 250, 300, 350]},
    {"name": "Frank", "expenses": [50, 60, 70, 80]},
    {"name": "Grace", "expenses": [300, 400, 500, 600]},
    {"name": "Helen", "expenses": [80, 90, 100, 110]},
    {"name": "Isaac", "expenses": [120, 140, 160, 180]},
    {"name": "Jack", "expenses": [50, 60, 70, 80]},
    {"name": "Katherine", "expenses": [90, 100, 110, 120]},
    {"name": "Liam", "expenses": [200, 250, 300, 350]},
    {"name": "Mary", "expenses": [60, 70, 80, 90]},
    {"name": "Nathan", "expenses": [300, 350, 400, 450]},
    {"name": "Olivia", "expenses": [80, 90, 100, 110]},
    {"name": "Paul", "expenses": [100, 110, 120, 130]},
    {"name": "Quinn", "expenses": [150, 160, 170, 180]},
    {"name": "Robert", "expenses": [70, 80, 90, 100]},
    {"name": "Sophia", "expenses": [180, 190, 200, 210]},
    {"name": "Thomas", "expenses": [110, 120, 130, 140]}
]

# Заданные критерии для фильтрации
criteria = {"expenses": 400}

def filter_and_calculate_expenses(users, criteria):
    filtered_users = [user for user in users if sum(user["expenses"]) >= criteria["expenses"]]
    total_expenses = sum(sum(user["expenses"]) for user in filtered_users)
    return filtered_users, total_expenses

filtered_users, total_expenses = filter_and_calculate_expenses(users, criteria)

print("Отфильтрованные пользователи:")
for user in filtered_users:
    print(f"{user['name']}: {sum(user['expenses'])}")

print(f"Общая сумма расходов отфильтрованных пользователей: {total_expenses}")

