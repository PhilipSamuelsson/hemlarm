import network
import urequests
import time
from machine import Pin, time_pulse_us

# WiFi Setup
SSID = "WIfI Name"  # Change this to your WiFi SSID
PASSWORD = "WiFi Password"  # Change this to your WiFi password
DEVICE_ID = "Name_Pico"  # Change this for each Pico W

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Connecting...")
    time.sleep(1)

print("Connected to WiFi:", wlan.ifconfig())

# Register this Pico with the Flask server
FLASK_URL = "http://XXX.XXX.X.XXX:5000/api" # Change this to your Flask server's IP

try:
    response = urequests.post(f"{FLASK_URL}/register_device", json={"device_id": DEVICE_ID})
    print("Registration response:", response.text)
    response.close()
except Exception as e:
    print("Error registering device:", e)

# Setup HC-SR04
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)
LED = Pin(15, Pin.OUT)

def get_distance():
    """Measures distance using the ultrasonic sensor"""
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    
    duration = time_pulse_us(ECHO, 1)
    distance = (duration * 0.0343) / 2  # Convert time to cm
    return distance

while True:
    distance = get_distance()
    print(f"Distance: {distance:.2f} cm")

    if distance > 0 and distance < 30:
        print("Motion detected! Turning LED ON")
        LED.on()

        # Send motion detection to Flask
        try:
            response = urequests.post(f"{FLASK_URL}/motion_detected", json={"device_id": DEVICE_ID, "distance": distance})
            print("Response:", response.text)
            response.close()
        except Exception as e:
            print("Error sending data:", e)

    else:
        LED.off()

    time.sleep(1)
