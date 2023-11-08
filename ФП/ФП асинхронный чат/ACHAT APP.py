import asyncio
import tkinter as tk
from tkinter import scrolledtext

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.room_name = ""
        self.reader = None
        self.writer = None

        # Окно приветствия
        self.welcome_label = tk.Label(root, text="Добро пожаловать в ACHAT! Введите название комнаты:")
        self.welcome_label.pack()

        self.room_name_entry = tk.Entry(root)
        self.room_name_entry.pack()

        self.join_button = tk.Button(root, text="Присоединиться", command=self.join_room)
        self.join_button.pack()

        # Окно чата
        self.chat_box = scrolledtext.ScrolledText(root)
        self.chat_box.pack()

        # Поле ввода сообщения
        self.message_entry = tk.Entry(root)
        self.message_entry.pack()

        # Кнопка отправки сообщения
        self.send_button = tk.Button(root, text="Отправить", command=self.send_message)
        self.send_button.pack()

    async def connect_to_server(self):
        try:
            self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу. Убедитесь, что сервер работает.")

    async def join_room(self):
        self.room_name = self.room_name_entry.get()
        self.room_name_entry.delete(0, 'end')
        await self.connect_to_server()
        if self.writer:
            self.writer.write(self.room_name.encode() + b'\n')
            asyncio.create_task(self.receive_messages())

    def send_message(self):
        if self.writer:
            message = self.message_entry.get()
            self.message_entry.delete(0, 'end')
            self.writer.write(f"{self.room_name}::{message}".encode() + b'\n')

    async def receive_messages(self):
        while True:
            data = await self.reader.read(100)
            message = data.decode().strip()
            self.chat_box.insert(tk.END, message + '\n')
            self.chat_box.see(tk.END)
            await asyncio.sleep(0.1)

async def main():
    root = tk.Tk()
    root.title("ACHAT Client")

    client = ChatClient(root)
    await client.join_room()  # Используйте await для вызова асинхронной функции
    root.mainloop()


if __name__ == '__main__':
    asyncio.run(main())
