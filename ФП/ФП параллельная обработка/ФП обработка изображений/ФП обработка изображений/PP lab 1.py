import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageEnhance, ImageOps
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import threading


def apply_filters_to_image(image_path, out_folder, filters, lock):
    try:
        with lock:
            print(f"Processing image: {image_path}")

        image = Image.open(image_path)
        filename, _ = os.path.splitext(os.path.basename(image_path))

        for suffix, filter_function in filters:
            if suffix == 'Sharpen':
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(filter_function)
            else:
                image = filter_function(image)

        out_path = os.path.join(out_folder, f'{filename}_Filtered.png')
        try:
            image.save(out_path)
            with lock:
                print(f"Image successfully processed: {image_path}")
        except Exception as e:
            error_message = f'Error saving {out_path}: {str(e)}'
            with lock:
                print(error_message)
                logging.error(error_message)

        image.close()

    except Exception as e:
        with lock:
            print(f'Error processing {image_path} with filters: {str(e)}')


def apply_filters(image_folder, out_folder, filters):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    tasks = []
    lock = threading.Lock()

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        if os.path.isfile(image_path) and image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            tasks.append((image_path, out_folder, filters, lock))

    with ThreadPoolExecutor() as executor:
        executor.map(lambda args: apply_filters_to_image(*args), tasks)

    # Wait for all threads to finish before destroying the lock
    executor.shutdown()

    print("Processing complete.")


def browse_folder(entry_widget):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(tk.END, folder_selected)


def apply_filters_callback():
    image_folder = entry_image_folder.get()
    out_folder = entry_output_folder.get()

    if image_folder and out_folder:
        selected_filters = [(filter_option, filter_function) for filter_option, filter_function in
                            zip(filter_options, filter_functions) if
                            filter_vars[filter_options.index(filter_option)].get()]

        if selected_filters:
            apply_filters(image_folder, out_folder, selected_filters)
            messagebox.showinfo("Завершено", "Фильтры успешно применены.")


root = tk.Tk()
root.title("Применение фильтров к изображениям")

filter_options = ["Sharpen", "Sepia", "Resize"]
filter_functions = [1.5, lambda image: ImageOps.colorize(image.convert('L'), "#3c1b17", "#bfa694"),
                    lambda image: image.resize((300, 300))]
filter_vars = [tk.IntVar() for _ in filter_options]

label_image_folder = tk.Label(root, text="Папка с изображениями:")
label_image_folder.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)

entry_image_folder = tk.Entry(root, width=50)
entry_image_folder.grid(row=0, column=1, padx=10, pady=5)

button_browse_image = tk.Button(root, text="Обзор", command=lambda: browse_folder(entry_image_folder))
button_browse_image.grid(row=0, column=2, padx=5, pady=5)

label_output_folder = tk.Label(root, text="Папка для сохранения:")
label_output_folder.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

entry_output_folder = tk.Entry(root, width=50)
entry_output_folder.grid(row=1, column=1, padx=10, pady=5)

button_browse_output = tk.Button(root, text="Обзор", command=lambda: browse_folder(entry_output_folder))
button_browse_output.grid(row=1, column=2, padx=5, pady=5)

label_filter = tk.Label(root, text="Выберите фильтры:")
label_filter.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)

for i, filter_option in enumerate(filter_options):
    filter_checkbutton = tk.Checkbutton(root, text=filter_option, variable=filter_vars[i])
    filter_checkbutton.grid(row=2 + i, column=1, padx=10, pady=2, sticky=tk.W)

button_apply_filters = tk.Button(root, text="Применить фильтры", command=apply_filters_callback)
button_apply_filters.grid(row=3, column=1, columnspan=3, pady=10)

root.mainloop()
