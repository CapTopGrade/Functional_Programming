import cv2
import numpy as np
import os
import csv
from tkinter import Tk, Button, Label, filedialog, Entry
import threading
import queue


def analyze_and_draw_objects(image, output_folder, file_name, draw_objects=True, min_area=0.5, max_area=100):
    flgFind = False

    # Сохранение результата в файл CSV
    csv_file_path = os.path.join(output_folder, "results.tsv")
    with open(csv_file_path, "a", newline="") as csvfile:
        fieldnames = ["File Name", "Object ID", "Object size", "Object area", "Object average color",
                      "Object brightness", "Center (x, y)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Инициализация уникального ID для объектов
        object_id = 1

        for contour in contours:
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            _, _, width, height = cv2.boundingRect(contour)
            center = (int(x), int(y))
            radius = int(radius)

            # Выделение области, соответствующей объекту
            roi = image[int(y) - radius:int(y) + radius, int(x) - radius:int(x) + radius]
            # Вычисление площади объекта
            area = cv2.contourArea(contour)

            ratio = width / height
            if ratio < 5:
                if min_area < area < max_area and height != 0 and width != 0:
                    # Выделение области, соответствующей объекту
                    roi = image[int(y) - radius:int(y) + radius, int(x) - radius:int(x) + radius]

                    # Ensure that roi is not empty before calculating mean
                    if roi.size > 0:
                        avg_color = np.mean(roi, axis=(1, 0))
                        brightness = np.mean(roi)

                        # Отрисовка красного круга, если параметр draw_objects=True
                        if draw_objects:
                            cv2.circle(image, center, radius * 2 + 5, (0, 0, 255), 2)

                            # Нанесение уникального ID рядом с красным кругом
                            cv2.putText(image, str(object_id), (int(x) + 10, int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (0, 0, 255), 2)

                        # Запись результатов в CSV
                        writer.writerow({
                            "File Name": file_name,
                            "Object ID": object_id,
                            "Object size": f"{width}x{height}",
                            "Object area": area,
                            "Object average color": avg_color,
                            "Object brightness": brightness,
                            "Center (x, y)": f"{center[0]}, {center[1]}"
                        })
                        flgFind = True
                        # Увеличение уникального ID для следующего объекта
                        object_id += 1
            else:
                if min_area < area < max_area and height != 0 and width != 0:
                    # Отрисовка красного круга, если параметр draw_objects=True
                    if draw_objects:
                        cv2.circle(image, center, radius * 2 + 5, (0, 0, 255), 2)
                        # Нанесение уникального ID рядом с красным кругом
                        cv2.putText(image, str("dobj"), (int(x) + 10, int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 0, 255), 2)

                    # Запись результатов в CSV
                    writer.writerow({
                        "File Name": file_name,
                        "Object ID": "Deformed_object",
                        "Object size": f"{width}x{height}",
                        "Object area": area,
                        "Object average color": "Deformed_object",
                        "Object brightness": "Deformed_object",
                        "Center (x, y)": f"{center[0]}, {center[1]}"
                    })
                    flgFind = True
                    # Увеличение уникального ID для следующего объекта

    return (image, flgFind)


def process_part(image, output_folder, file_name, draw_objects=True):
    analyzed_image, flg = analyze_and_draw_objects(image, output_folder, file_name, draw_objects=draw_objects)

    if flg:
        # Save the analyzed image with objects drawn
        analyzed_part_path = os.path.join(output_folder, f"analyzed_{file_name}")
        cv2.imwrite(analyzed_part_path, analyzed_image)


# Определение очереди для хранения задач обработки изображений
image_queue = queue.Queue()


def process_part_threaded(image, output_folder, file_name, draw_objects=True):
    analyzed_image, flg = analyze_and_draw_objects(image, output_folder, file_name, draw_objects=draw_objects)

    if flg:
        # Save the analyzed image with objects drawn
        analyzed_part_path = os.path.join(output_folder, f"analyzed_{file_name}")
        cv2.imwrite(analyzed_part_path, analyzed_image)


# Определение функции для потока обработки изображений
def process_image_worker():
    while True:
        try:
            # Получение задачи из очереди
            image, output_folder, file_name, draw_objects = image_queue.get_nowait()

            # Обработка изображения
            process_part_threaded(image, output_folder, file_name, draw_objects=draw_objects)

            # Пометка задачи как выполненной
            image_queue.task_done()
        except queue.Empty:
            # Перехватываем исключение, если очередь пуста
            pass


# Создание и запуск потоков обработки изображений
num_threads = 8  # Задайте желаемое количество потоков

for _ in range(num_threads):
    thread = threading.Thread(target=process_image_worker)
    thread.daemon = True  # Позволяет завершить программу, не дожидаясь завершения всех потоков
    thread.start()


# Изменения в функции process_part
def process_part(image, output_folder, file_name, draw_objects=True):
    # Добавление задачи в очередь для каждой части изображения
    image_queue.put((image, output_folder, file_name, draw_objects))


def split_and_analyze_image(input_image_path, output_folder, part_size=(256, 256), draw_objects=True,
                            min_area=0.5, max_area=100):
    # Read the input image
    image = cv2.imread(input_image_path)

    # Get the dimensions of the input image
    height, width, _ = image.shape

    # Create a folder for saving results
    if output_folder == "":
        output_folder = "results"  # Use a default name if not provided
    output_path = os.path.join(os.path.dirname(input_image_path), output_folder)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Create a CSV file for results
    csv_file_path = os.path.join(output_path, "results.tsv")
    with open(csv_file_path, "w", newline="") as csvfile:
        fieldnames = ["File Name", "Object ID", "Object size", "Object area", "Object average color",
                      "Object brightness", "Center (x, y)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

    # Split the image into parts
    for i in range(0, height, part_size[0]):
        for j in range(0, width, part_size[1]):
            # Extract the part from the original image
            part = image[i:i + part_size[0], j:j + part_size[1]]

            # Save each part separately
            file_name = f"part_{i // part_size[0]}_{j // part_size[1]}.jpg"
            part_path = os.path.join(output_path, file_name)
            cv2.imwrite(part_path, part)

            # Process each part
            process_part(part, output_path, file_name, draw_objects=draw_objects)


def get_part_size():
    part_size_window = Tk()
    part_size_window.title("Enter Part Size")

    width_label = Label(part_size_window, text="Width:")
    width_label.grid(row=0, column=0, padx=5, pady=5)

    width_entry = Entry(part_size_window)
    width_entry.grid(row=0, column=1, padx=5, pady=5)

    height_label = Label(part_size_window, text="Height:")
    height_label.grid(row=1, column=0, padx=5, pady=5)

    height_entry = Entry(part_size_window)
    height_entry.grid(row=1, column=1, padx=5, pady=5)

    def get_size():
        width = int(width_entry.get())
        height = int(height_entry.get())
        part_size_window.destroy()
        split_and_analyze_image(input_image_path, output_folder, part_size=(width, height))

    confirm_button = Button(part_size_window, text="Confirm", command=get_size)
    confirm_button.grid(row=2, column=0, columnspan=2, pady=10)

    part_size_window.mainloop()


def browse_image():
    global input_image_path
    input_image_path = filedialog.askopenfilename()
    file_label.config(text=f"Selected Image: {os.path.basename(input_image_path)}")


# Global variables
input_image_path = ""
output_folder = ""

# Create Tkinter window
root = Tk()
root.geometry("200x250")
root.title("Image Analysis")

# Browse Button
browse_button = Button(root, text="Browse Image", command=browse_image)
browse_button.pack(pady=10)

# Selected File Label
file_label = Label(root, text="Selected Image: None")
file_label.pack()

# Analyze Button
analyze_button = Button(root, text="Analyze Image", command=get_part_size)
analyze_button.pack(pady=10)

# Result Label
result_label = Label(root, text="")
result_label.pack()

image_queue.join()

# Run the Tkinter event loop
root.mainloop()
