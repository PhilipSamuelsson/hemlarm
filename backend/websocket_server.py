import asyncio
import websockets
import json
import requests

# Flask API URL
FLASK_URL = "https://hemlarm.onrender.com/api/motion_detected"

# WebSocket Server Config
HOST = "0.0.0.0"  # Allow connections from any device on the network
PORT = 8765

# Send data to Flask API
async def send_to_backend(data):
    try:
        response = requests.post(FLASK_URL, json=data)
        if response.status_code == 201:
            print(f"✅ Data sent to Flask: {response.text}")
        else:
            print(f"⚠️ Flask API responded with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error sending to Flask: {e}")

# Handle incoming WebSocket messages
async def handle_client(websocket):
    print(f"🔗 New connection from {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"📩 Received data: {message}")

            # Try parsing JSON
            try:
                data = json.loads(message)
                if "device_id" in data and "distance" in data:
                    await send_to_backend(data)  # Send to Flask API
                else:
                    print("⚠️ Invalid JSON format")
            except json.JSONDecodeError:
                print("❌ Could not parse JSON data")

    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Connection closed: {websocket.remote_address}")

# Start WebSocket Server
async def start_server():
    async with websockets.serve(handle_client, HOST, PORT):
        print(f"🚀 WebSocket server running on {HOST}:{PORT}")
        await asyncio.Future()  # Keeps the server running

# Run server
if __name__ == "__main__":
    asyncio.run(start_server())