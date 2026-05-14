# lcd_display.py - LCD display for direction and CPU temperature
from time import sleep
import RPi.GPIO as GPIO
import threading
from gpiozero import CPUTemperature

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LCD pins
RS = 27
E = 22
D4 = 25
D5 = 24
D6 = 23
D7 = 18

# Setup LCD pins
for pin in [RS, E, D4, D5, D6, D7]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)

# Global variables
current_direction = "clear"
current_distance = 0
_running = True

# Initialize CPU temperature sensor
cpu = CPUTemperature()

# Default thresholds (these should match your constants)
EMERGENCY_DIST = 12  # cm
THRESHOLD_MEDIUM = 30  # cm

# LCD Functions
def pulse_enable():
    GPIO.output(E, True)
    sleep(0.0005)
    GPIO.output(E, False)

def send_nibble(data):
    GPIO.output(D4, (data >> 0) & 1)
    GPIO.output(D5, (data >> 1) & 1)
    GPIO.output(D6, (data >> 2) & 1)
    GPIO.output(D7, (data >> 3) & 1)
    pulse_enable()

def send_byte(data, mode):
    GPIO.output(RS, mode)
    send_nibble(data >> 4)
    send_nibble(data & 0x0F)
    sleep(0.002)

def lcd_init():
    sleep(0.050)
    GPIO.output(RS, False)
    
    for _ in range(3):
        send_nibble(0x03)
        sleep(0.005)
    
    send_nibble(0x02)
    sleep(0.001)
    
    send_byte(0x28, 0)
    sleep(0.002)
    send_byte(0x0C, 0)
    sleep(0.002)
    send_byte(0x06, 0)
    sleep(0.002)
    send_byte(0x01, 0)
    sleep(0.003)
    
    print("LCD initialized")

def lcd_clear():
    send_byte(0x01, 0)
    sleep(0.003)

def lcd_print(text, line=0, start_pos=0):
    if line == 0:
        send_byte(0x80 + start_pos, 0)
    else:
        send_byte(0xC0 + start_pos, 0)
    
    for char in text:
        send_byte(ord(char), 1)

def update_display():
    """Update LCD with CPU temp and current direction"""
    global current_direction, current_distance
    
    # Get CPU temperature
    temp = cpu.temperature
    
    # Clear and update LCD
    lcd_clear()
    
    # Line 1: CPU temperature
    lcd_print(f"CPU:{temp:.0f}C", 0, 0)
    
    # Line 1 right side: Direction
    if current_direction == "emergency":
        lcd_print("EMG", 0, 10)
    elif current_direction != "clear":
        lcd_print(f"{current_direction}", 0, 10)
    else:
        lcd_print("clear", 0, 10)
    
    # Line 2: Distance
    if current_distance > 0:
        lcd_print(f"{current_distance:.0f}cm", 1, 0)
    else:
        lcd_print("---", 1, 0)

def display_thread():
    """Background thread to update display"""
    while _running:
        update_display()
        sleep(0.2)

def start_display():
    """Start the LCD display"""
    lcd_init()
    display_t = threading.Thread(target=display_thread, daemon=True)
    display_t.start()
    print("LCD Display started")

def stop_display():
    """Stop the LCD display"""
    global _running
    _running = False
    lcd_clear()
    GPIO.cleanup()
    print("LCD Display stopped")

def set_direction(direction, distance=0):
    """Set current direction from main code"""
    global current_direction, current_distance
    current_direction = direction
    current_distance = distance

def get_cpu_temp():
    """Get current CPU temperature"""
    return cpu.temperature

# THIS IS THE FUNCTION YOUR MAIN CODE IS CALLING
# It needs to be in the global namespace when you import lcd
def determine_direction(zones):
    """Determine direction and distance from zones for LCD display"""
    front = zones.get('front')
    left_side = zones.get('left_side')
    right_side = zones.get('right_side')
    left_front = zones.get('left_front')
    right_front = zones.get('right_front')
    emg = zones.get('emergency')
    
    # Emergency has priority
    if emg is not None and emg < EMERGENCY_DIST:
        return "emergency", emg
    
    # Check front
    if front is not None and front < THRESHOLD_MEDIUM:
        return "front", front
    
    # Check sides
    if left_side is not None and left_side < THRESHOLD_MEDIUM:
        return "left", left_side
    
    if right_side is not None and right_side < THRESHOLD_MEDIUM:
        return "right", right_side
    
    # Check front sides
    if left_front is not None and left_front < THRESHOLD_MEDIUM:
        return "left", left_front
    
    if right_front is not None and right_front < THRESHOLD_MEDIUM:
        return "right", right_front
    
    # Clear path
    return "clear", 0
