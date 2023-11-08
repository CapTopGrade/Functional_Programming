students = [
    {"name": "Alice", "age": 20, "grades": [85, 90, 88, 92]},
    {"name": "Bob", "age": 22, "grades": [78, 89, 76, 85]},
    {"name": "Charlie", "age": 21, "grades": [92, 95, 88, 94]},
    {"name": "David", "age": 20, "grades": [75, 80, 78, 82]},
    {"name": "Eve", "age": 23, "grades": [88, 90, 92, 95]},
    {"name": "Frank", "age": 22, "grades": [80, 85, 82, 89]},
    {"name": "Grace", "age": 21, "grades": [95, 97, 93, 98]},
    {"name": "Hank", "age": 20, "grades": [70, 75, 78, 72]},
    {"name": "Ivy", "age": 24, "grades": [91, 94, 92, 90]},
    {"name": "Jack", "age": 21, "grades": [84, 87, 85, 89]},
    {"name": "Karen", "age": 22, "grades": [76, 78, 79, 81]},
    {"name": "Liam", "age": 20, "grades": [88, 90, 86, 92]},
    {"name": "Mia", "age": 23, "grades": [82, 85, 88, 89]},
    {"name": "Noah", "age": 21, "grades": [91, 94, 95, 97]},
    {"name": "Olivia", "age": 20, "grades": [75, 78, 80, 82]},
    {"name": "Parker", "age": 22, "grades": [88, 90, 92, 94]},
    {"name": "Quinn", "age": 21, "grades": [78, 80, 82, 84]},
    {"name": "Riley", "age": 20, "grades": [92, 95, 88, 94]},
    {"name": "Sam", "age": 23, "grades": [70, 75, 78, 72]},
    {"name": "Taylor", "age": 22, "grades": [85, 88, 89, 90]}
]


# Функция для фильтрации данных
def filter_students(students, min_age=None, grade_position=None):
    filtered_students = students.copy()
    if min_age is not None:
        filtered_students = [student for student in filtered_students if student["age"] == min_age]
    if grade_position is not None:
        filtered_students = [student for student in filtered_students if len(student["grades"]) > grade_position]
    return filtered_students

# Функция для вычисления среднего балла студента
def calculate_student_average(grades):
    return sum(grades) / len(grades) if grades else 0

# Функция для вычисления общего среднего балла по всем студентам
def calculate_overall_average(students):
    all_grades = [grade for student in students for grade in student["grades"]]
    return sum(all_grades) / len(all_grades) if all_grades else 0

# Функция для нахождения студента с самым высоким средним баллом
def find_top_student(students):
    if not students:
        return None
    return max(students, key=lambda student: calculate_student_average(student["grades"]))

# Пример использования функций
grade_position_to_filter = 2 
filtered_students = filter_students(students, min_age=20, grade_position=grade_position_to_filter)
for student in filtered_students:
    print(f"{student['name']}: {calculate_student_average(student['grades'])}")

overall_average = calculate_overall_average(filtered_students)
print(f"Общий средний балл по всем студентам: {overall_average}")

top_student = find_top_student(filtered_students)
print(f"Студент с самым высоким средним баллом: {top_student['name']}")
