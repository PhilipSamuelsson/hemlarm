from machine import Pin, time_pulse_us
import time

# Setup Pins
TRIG = Pin(3, Pin.OUT)   # HC-SR04 Trigger (GPIO 3)
ECHO = Pin(2, Pin.IN)    # HC-SR04 Echo (GPIO 2, using voltage divider)
LED = Pin(15, Pin.OUT)   # LED on GPIO 15

def get_distance():
    """Measures distance using the ultrasonic sensor"""
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    duration = time_pulse_us(ECHO, 1)  # Measure echo time
    distance = (duration * 0.0343) / 2  # Convert time to distance (cm)
    
    return distance

print("Ultrasonic sensor active...")

while True:
    distance = get_distance()
    print(f"Distance: {distance:.2f} cm")

    if distance > 0 and distance < 30:  # If object is within 30 cm
        print("Object detected! Turning LED ON")
        LED.on()
    else:
        LED.off()

    time.sleep(0.5)  # Delay before the next measurement
