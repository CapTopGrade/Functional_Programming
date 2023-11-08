import asyncio

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.rooms = {}

    async def handle_client(self, reader, writer):
        peername = writer.get_extra_info('peername')
        client_name = await self.get_unique_client_name(reader, writer)
        room_name = await self.get_room_name(reader, writer)

        client = (reader, writer, client_name, room_name)
        self.clients[peername] = client

        await self.broadcast(f"{client_name} присоединился к комнате {room_name}.", room_name, exclude=peername)

        try:
            while True:
                data = await reader.read(100)
                message = data.decode().strip()
                if not data:
                    break

                if message.startswith('/'):
                    await self.handle_command(client, message)
                else:
                    await self.handle_message(client, message)
        except asyncio.CancelledError:
            pass
        finally:
            del self.clients[peername]
            await self.broadcast(f"{client_name} покинул комнату.", room_name)

    async def get_client_name(self, reader, writer):
        writer.write("Введите ваше имя: ". encode())
        await writer.drain()
        data = await reader.read(100)
        return data.decode().strip()
    
    async def get_unique_client_name(self, reader, writer):
        while True:
            writer.write("Введите уникальное имя: ".encode())
            await writer.drain()
            data = await reader.read(100)
            client_name = data.decode().strip()
            if await self.is_unique_name(client_name):
                return client_name
    
    async def send_private_message(self, sender, target_name, message):
        for client in self.clients.values():
            if client[2] == target_name:
                client[1].write(f"Лично от {sender[2]}: {message}".encode() + b'\n')
                await client[1].drain()

    async def get_room_name(self, reader, writer):
        writer.write("Введите название комнаты: ". encode())
        await writer.drain()
        data = await reader.read(100)
        room_name = data.decode().strip()
        if room_name not in self.rooms:
            self.rooms[room_name] = set()
        self.rooms[room_name].add(writer.get_extra_info('peername'))
        return room_name

    async def handle_message(self, sender, message):
        room_name = sender[3]
        sender_name = sender[2]
        await self.broadcast(f"{sender_name}: {message}", room_name, exclude=sender[1].get_extra_info('peername'))

    async def broadcast(self, message, room_name, exclude=None):
        for client in self.clients.values():
            if client[3] == room_name and client[1].get_extra_info('peername') != exclude:
                client[1].write(message.encode() + b'\n')
                await client[1].drain()

    async def handle_command(self, sender, command):
        if command.startswith('/whisper'):
            parts = command.split(' ')
            if len(parts) >= 3:
                target_name = parts[1]
                target_message = ' '.join(parts[2:])
                await self.send_private_message(sender, target_name, target_message)

    async def start_server(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

        async with server:
            await server.serve_forever()

    async def is_unique_name(self, client_name):
        for client in self.clients.values():
            if client[2] == client_name:
                return False
        return True
    

if __name__ == '__main__':
    chat_server = ChatServer('127.0.0.1', 8888)
    asyncio.run(chat_server.start_server())
