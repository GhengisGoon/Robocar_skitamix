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
    
    # Line 2: Distance (convert cm to mm to match your main code)
    if current_distance > 0:
        # Distance comes in cm from sensor, convert to mm for display
        distance_mm = current_distance * 10
        lcd_print(f"{distance_mm:.0f}mm", 1, 0)
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
    current_distance = distance  # distance is in cm from your sensor

def get_cpu_temp():
    """Get current CPU temperature"""
    return cpu.temperature
