import os
import concurrent.futures
from PIL import Image, ImageFilter



def apply_sharpen_filter(image):
    sharpened_image = image.filter(ImageFilter.SHARPEN)
    return sharpened_image


def apply_sepia_filter(image):
    width, height = image.size
    sepia_image = Image.new('RGB', (width, height))

    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            new_r = min(255, gray + 40)
            new_g = min(255, gray + 20)
            new_b = max(0, gray - 20)
            sepia_image.putpixel((x, y), (new_r, new_g, new_b))

    return sepia_image


def apply_resize_filter(image, new_size=(800, 600)):

    resized_image = image.resize(new_size, Image.ANTIALIAS)
    return resized_image


# Загрузка изображений
def load_images(input_folder):
    images = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".JPG"):
            image = Image.open(os.path.join(input_folder, filename))
            images.append(image)
    return images

# Сохранение обработанных изображений
def save_image(image, output_folder, filename):
    image.save(os.path.join(output_folder, filename))

def process_image(image, filters, output_folder):
    try:
        for filter_name, filter_function in filters.items():
            filtered_image = filter_function(image)
            save_image(filtered_image, output_folder, f"{filter_name}_{os.path.basename(image.filename)}")
            print(f"Изображение {os.path.basename(image.filename)} обработано и сохранено.")
    except Exception as e:
        # Обработка ошибок исключений, например, запись в журнал
        print(f"Ошибка при обработке изображения: {str(e)}")

        
if __name__ == "__main__":
    input_folder = "input_images"
    output_folder = "output_images"
    filters = {
        "sharpen": apply_sharpen_filter,
        "sepia": apply_sepia_filter,
        "resize": apply_resize_filter,
    }

    os.makedirs(output_folder, exist_ok=True)
    images = load_images(input_folder)

     # Создаем пул потоков
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        tasks = []

        # Заполняем список задач
        for image in images:
            task = executor.submit(process_image, image, filters, output_folder)
            tasks.append(task)

        # Ожидаем завершения всех задач
        concurrent.futures.wait(tasks)

    print("Все задачи обработаны.")

