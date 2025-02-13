import network
import urequests
import time
from machine import Pin, time_pulse_us

# 🔹 WiFi Credentials
SSID = "Wifi_Name" #Use your own wifi name
PASSWORD = "Password" #Use your own wifi password

# 🔹 Firebase Realtime Database URL (Replace with your Firebase URL)
FIREBASE_URL = "https://home-alarm-c3d76-default-rtdb.europe-west1.firebasedatabase.app/motion.json"

# 🔹 Pico Device ID (Change for each device)
DEVICE_ID = "Philips Pico"

# 🔹 Setup HC-SR04 Ultrasonic Sensor & LED
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)
LED = Pin(15, Pin.OUT)

# 🔹 Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("🔄 Connecting to WiFi...")
        time.sleep(1)
    
    print(f"✅ Connected! IP Address: {wlan.ifconfig()[0]}")

# 🔹 Measure distance with HC-SR04
def get_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    duration = time_pulse_us(ECHO, 1, 30000)  # 30ms timeout
    if duration < 0:
        return None  # No valid measurement

    distance = (duration * 0.0343) / 2  # Convert time to cm
    return distance

# 🔹 Send motion data to Firebase
def send_motion_data(distance):
    data = {
        "device_id": DEVICE_ID,
        "distance": distance,
        "timestamp": time.time()  # Unix timestamp
    }
    try:
        response = urequests.post(FIREBASE_URL, json=data)
        print(f"✅ Motion data sent to Firebase: {response.text}")
        response.close()
    except Exception as e:
        print(f"❌ Error sending data: {e}")

# 🔹 Main Program
connect_wifi()

while True:
    distance = get_distance()
    if distance is not None and distance < 30:  # Motion detected!
        print(f"⚠️ Motion detected! Distance: {distance:.2f} cm")
        LED.on()
        send_motion_data(distance)
    else:
        LED.off()

    time.sleep(1)  # Adjust based on request limits
