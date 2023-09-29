import asyncio
import websockets
import json
import uuid

connected_clients = {}  # Dictionary to store connected clients with their username as key and websocket as value

async def server(websocket, path):
    client_id = uuid.uuid4()
    username = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "register":
                username = data["data"]
                if username not in connected_clients:
                    connected_clients[username] = websocket
                    await notify_users()
                else:
                    await websocket.send(json.dumps({"type": "error", "data": "Username is already taken"}))
            elif data["type"] == "message" and username:
                recipient = data["recipient"]
                if recipient in connected_clients:
                    await connected_clients[recipient].send(json.dumps({"type": "message", "sender": username, "data": data["data"]}))
    finally:
        if username:
            connected_clients.pop(username, None)
            await notify_users()

async def notify_users():
    user_list = list(connected_clients.keys())
    await asyncio.gather(
        *[client.send(json.dumps({"type": "users", "data": user_list})) for client in connected_clients.values()]
    )

start_server = websockets.serve(server, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
