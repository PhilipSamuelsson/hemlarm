import network
import urequests
import time
import ujson
from machine import Pin, time_pulse_us

# 🔹 WiFi Credentials
SSID = "Name of wifi network"
PASSWORD = "Password"

# 🔹 Flask API URL
FLASK_API = "https://hemlarm.onrender.com/api"

# 🔹 Pico Device ID (Unique)
DEVICE_ID = "Name of pico device"

# 🔹 Setup HC-SR04 Ultrasonic Sensor & LED
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)
LED = Pin(15, Pin.OUT)

# 🔹 WiFi Connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    timeout = 15
    for i in range(timeout):
        if wlan.isconnected():
            print(f"✅ Connected to WiFi! IP: {wlan.ifconfig()[0]}")
            return True
        print(f"🔄 Connecting to WiFi ({i+1}/{timeout})...")
        time.sleep(1)

    print("❌ Failed to connect to WiFi!")
    return False

# 🔹 Register Device with Flask API
def register_device():
    url = f"{FLASK_API}/register_device"
    data = {"device_id": DEVICE_ID, "name": "Motion Sensor"}
    
    try:
        response = urequests.post(url, json=data)
        if response.status_code == 201 or response.status_code == 200:
            print(f"✅ Device registered: {DEVICE_ID}")
        else:
            print(f"⚠️ Registration failed, status {response.status_code}: {response.text}")
        response.close()
    except Exception as e:
        print(f"❌ Error registering device: {e}")

# 🔹 Measure distance with HC-SR04
def get_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    duration = time_pulse_us(ECHO, 1, 30000)
    if duration < 0:
        return None

    distance = (duration * 0.0343) / 2
    
    if distance < 2 or distance > 200:
        return None
    
    return distance

# 🔹 Send Motion Data to Flask API
def send_motion_data(distance, motion_detected):
    url = f"{FLASK_API}/motion_detected"
    data = {
        "device_id": DEVICE_ID,
        "distance": round(distance, 2),
        "motion_detected": motion_detected,
        "timestamp": time.time()
    }
    
    try:
        response = urequests.post(url, json=data)
        if response.status_code == 201:
            print(f"✅ Data sent: {data}")
        else:
            print(f"⚠️ Flask API error {response.status_code}: {response.text}")
        response.close()
    except Exception as e:
        print(f"❌ Error sending data: {e}")

# 🔹 Main Program
if connect_wifi():
    register_device()  # Register device at startup

    previous_distance = None

    while True:
        distance = get_distance()
        if distance is not None:
            motion_detected = distance < 30  # Motion threshold
            
            # Log only if significant change or motion detected
            if previous_distance is None or abs(previous_distance - distance) > 5 or motion_detected:
                send_motion_data(distance, motion_detected)

                if motion_detected:
                    LED.on()
                else:
                    LED.off()

                previous_distance = distance

        time.sleep(1)  # Adjust based on API rate limits
else:
    print("❌ Exiting program, no WiFi connection.")
