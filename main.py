import asyncio
import json
import math
import time

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# fastapi initial
app = FastAPI(title="DLR Drone Telemetry Server")

# allow Cross-Origin Resource Sharing (CORS) so frontend HTML can connect to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# base coordinates of DLR BS
BASE_LAT = 52.315
BASE_LON = 10.550
BASE_ALT = 100.0  # Base altitude in meters


async def generate_drone_data():
    """
    Simulates real-time drone telemetry data.
    Generates a circular flight path around the base coordinates.
    """
    while True:
        # use the current time to calculate smooth mathematical movements
        t = time.time()

        # calculate new position (Circular patrol path)
        radius = 0.003  # Roughly 300 meters radius
        current_lat = BASE_LAT + (math.sin(t / 5) * radius)
        current_lon = BASE_LON + (math.cos(t / 5) * radius)

        # altitude varies smoothly between 80m and 120m
        current_alt = BASE_ALT + (math.sin(t / 10) * 20)

        # create the data payload
        telemetry_data = {
            "timestamp": round(t, 2),
            "latitude": round(current_lat, 6),
            "longitude": round(current_lon, 6),
            "altitude": round(current_alt, 2),
        }

        yield telemetry_data

        # pause for 0.1 seconds (This creates our 10Hz update rate)
        await asyncio.sleep(0.1)


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """
    WebSocket endpoint that streams the drone data to any connected client (like AR/VR headsets or web maps).
    """
    await websocket.accept()
    print("New client connected to telemetry stream!")

    try:
        # Continuously generate and send data
        async for data in generate_drone_data():
            await websocket.send_text(json.dumps(data))
    except Exception as e:
        print(f"Client disconnected.")
