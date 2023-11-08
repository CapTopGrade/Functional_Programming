import asyncio

async def send_message(reader, writer, room_name):
    while True:
        message = input("Введите сообщение: ")
        if message.lower() == 'exit':
            break  # При вводе "exit" завершить отправку сообщений
        writer.write(f"{room_name}::{message}".encode() + b'\n')
        await writer.drain()

async def send_private_message(reader, writer):
    while True:
        target_name = input("Введите имя получателя (для личного сообщения): ")
        if target_name.lower() == 'exit':
            break  # При вводе "exit" завершить отправку личных сообщений
        message = input("Введите личное сообщение: ")
        writer.write(f"/whisper {target_name} {message}".encode() + b'\n')
        await writer.drain()

async def main():
    try:
        room_name = input("Введите название комнаты: ")
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        writer.write(room_name.encode() + b'\n')
        await writer.drain()
        asyncio.create_task(send_message(reader, writer, room_name))
        await send_private_message(reader, writer)
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу. Убедитесь, что сервер работает.")

if __name__ == '__main__':
    asyncio.run(main())
