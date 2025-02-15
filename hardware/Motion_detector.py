import network
import urequests
import time
from machine import Pin, time_pulse_us

# 🔹 WiFi Credentials
SSID = "Name"
PASSWORD = "Password"

# 🔹 Firebase Realtime Database URL
FIREBASE_URL = "https://home-alarm-c3d76-default-rtdb.europe-west1.firebasedatabase.app"

# 🔹 Pico Device ID (unikt per enhet)
DEVICE_ID = "Philips_Pico"

# 🔹 Setup HC-SR04 Ultrasonic Sensor & LED
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)
LED = Pin(15, Pin.OUT)

# 🔹 WiFi-anslutning
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    timeout = 15  # Timeout för att ansluta till WiFi (sekunder)
    for i in range(timeout):
        if wlan.isconnected():
            print(f"✅ Ansluten till WiFi! IP: {wlan.ifconfig()[0]}")
            return True
        print(f"🔄 Försöker ansluta till WiFi ({i+1}/{timeout})...")
        time.sleep(1)

    print("❌ Misslyckades att ansluta till WiFi!")
    return False  # Om anslutning misslyckas

# 🔹 Funktion för att registrera enheten i "devices"
def register_device():
    url = f"{FIREBASE_URL}/devices/{DEVICE_ID}.json"
    data = {
        "device_id": DEVICE_ID,
        "status": "connected",
        "last_seen": time.time()
    }
    
    try:
        response = urequests.put(url, json=data)
        if response.status_code == 200:
            print(f"✅ Enhet registrerad i Firebase: {DEVICE_ID}")
        else:
            print(f"⚠️ Misslyckades att registrera enhet, statuskod: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"❌ Fel vid HTTP-förfrågan: {e}")

# 🔹 Funktion för att mäta avstånd
def get_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    duration = time_pulse_us(ECHO, 1, 30000)  # Timeout 30ms
    if duration < 0:
        print("⚠️ Misslyckad avståndsmätning")
        return None

    distance = (duration * 0.0343) / 2  # Omvandla tid till cm
    
    if distance < 2 or distance > 200:  # Filtrera bort osäkra värden
        print("⚠️ Ogiltigt avstånd mätt, ignorerar...")
        return None
    
    return distance

# 🔹 Funktion för att skicka data till "logs"
def send_motion_data(distance, motion_detected):
    url = f"{FIREBASE_URL}/logs.json"
    data = {
        "device_id": DEVICE_ID,
        "distance": round(distance, 2),
        "motion_detected": motion_detected,
        "timestamp": time.time()
    }
    
    try:
        response = urequests.post(url, json=data)
        if response.status_code == 200:
            print(f"✅ Data skickad till Firebase: {response.text}")
        else:
            print(f"⚠️ Misslyckades att skicka data, statuskod: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"❌ Fel vid HTTP-förfrågan: {e}")

# 🔹 Starta programmet
if connect_wifi():
    register_device()  # Registrera enheten vid start
    previous_distance = None  # För att undvika onödiga loggar

    while True:
        distance = get_distance()
        
        if distance is not None:
            motion_detected = distance < 30  # Definiera rörelse
            
            # Endast logga om avståndet ändrats mer än 5 cm eller rörelse upptäcks
            if previous_distance is None or abs(previous_distance - distance) > 5 or motion_detected:
                send_motion_data(distance, motion_detected)
                
                # Tänd LED om rörelse upptäcks
                if motion_detected:
                    print(f"🚨 Rörelse upptäckt! Avstånd: {distance:.2f} cm")
                    LED.on()
                else:
                    print(f"🛡️ Ingen rörelse. Avstånd: {distance:.2f} cm")
                    LED.off()
                
                previous_distance = distance  # Uppdatera föregående värde
        else:
            LED.off()  # Om ingen data fås, släck LED

        time.sleep(1)  # Vänta 1 sekund innan nästa mätning
else:
    print("❌ Avbryter program, ingen WiFi-anslutning.")

