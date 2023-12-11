import asyncio
import websockets


class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.rooms = {}

    async def handle_client(self, websocket: websockets.WebSocketServerProtocol) -> None:
        peername = websocket.remote_address
        client_name = await self.get_unique_client_name(websocket)
        room_name = await self.get_room_name(websocket)

        try:
            client = (websocket, client_name, room_name)
            self.clients[peername] = client

            await self.broadcast(f"{client_name} присоединился к комнате {room_name}.", room_name, exclude=peername)

            async for message in websocket:
                await self.handle_message(client, message)
        except websockets.exceptions.ConnectionClosedOK:
            pass
        finally:
            if peername in self.clients:
                del self.clients[peername]
            await self.broadcast(f"{client_name} покинул комнату.", room_name)

    async def create_room(self, client, room_name, user_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = set()

        self.rooms[room_name].add(client[0].remote_address)
        await self.broadcast(f"{user_name} создал комнату {room_name}.", room_name)

    async def join_room(self, client, room_name, user_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = set()

        self.rooms[room_name].add(client[0].remote_address)
        await self.broadcast(f"{user_name} присоединился к комнате {room_name}.", room_name)

    async def get_unique_client_name(self, websocket):
        while True:
            await websocket.send("Введите уникальное имя: ")
            client_name = (await websocket.recv()).strip()
            if await self.is_unique_name(client_name):
                return client_name

    async def get_room_name(self, websocket):
        await websocket.send("Введите название комнаты: ")
        room_name = (await websocket.recv()).strip()
        self.rooms.setdefault(room_name, set())
        self.rooms[room_name].add(websocket.remote_address)
        return room_name

    async def handle_message(self, sender, message):
        room_name = sender[2]
        sender_name = sender[1]

        if message.startswith('/whisper'):
            parts = message.split(' ')
            if len(parts) >= 3:
                target_name = parts[1]
                target_message = ' '.join(parts[2:])
                target_client = next((client for client in self.clients.values() if client[1] == target_name), None)
                if target_client:
                    await self.send_private_message(sender, target_client, target_message)
        else:
            await self.broadcast(f"{room_name}: {sender_name}: {message}", room_name, exclude=sender)

    async def broadcast(self, message, room_name, exclude=None):
        for client in self.clients.values():
            if client[2] == room_name and client[0].remote_address != exclude:
                try:
                    await client[0].send(message)
                    print(f"Sent message to {client[1]} in room {room_name}")
                except Exception as e:
                    print(f"Error sending message to {client[1]}: {str(e)}")

    async def handle_message(self, sender, message):
        room_name = sender[2]
        sender_name = sender[1]

        if message.startswith('/whisper'):
            parts = message.split(' ')
            if len(parts) >= 3:
                target_name = parts[1]
                target_message = ' '.join(parts[2:])
                target_client = next((client for client in self.clients.values() if client[1] == target_name), None)
                if target_client:
                    await self.send_private_message(sender, target_client, target_message)
        else:
            await self.broadcast(f"{room_name}: {sender_name}: {message}", room_name, exclude=sender)

    async def send_private_message(self, sender, target_client, message):
        target_websocket = target_client[0]
        sender_name = sender[1]

        if sender != target_client:
            await target_websocket.send(f"Лично от {sender_name}: {message}")
            await sender[0].send(f"Лично для {target_client[1]}: {message}")

    async def handle_room_action(self, sender, data):
        action = data['action']
        if action == 'join':
            room_name = data['roomName']
            user_name = data['userName']
            await self.join_room(sender, room_name, user_name)
        elif action == 'create':
            room_name = data['roomName']
            user_name = data['userName']
            await self.create_room(sender, room_name, user_name)

    async def handle_whisper(self, sender, data):
        target_name = data['targetName']
        target_message = data['message']
        if target_name in [client[1] for client in self.clients.values()]:
            target_client = next(client for client in self.clients.values() if client[1] == target_name)
            await self.send_private_message(sender, target_client, target_message)
            await self.send_private_message(sender, target_client, target_message)

            await self.broadcast(f"Лично для {target_name}: {target_message}", sender[2], exclude=target_client)

    async def is_unique_name(self, client_name):
        return all(client[1] != client_name for client in self.clients.values())

    async def start_server(self):
        server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"Server started. Listening on {self.host}:{self.port}")

        await server.wait_closed()


if __name__ == '__main__':
    chat_server = ChatServer('127.0.0.1', 8888)
    asyncio.run(chat_server.start_server())
