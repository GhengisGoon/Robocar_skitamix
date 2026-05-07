import smbus2
import time
from constants import MOTOR_I2C_ADDRESS, SPEED_SLOW, SPEED_MEDIUM, TURN_TIME, EMERGENCY_REVERSE_TIME

bus = smbus2.SMBus(1)


def _send_motors(m1, m2):
    m1 = max(-255, min(255, m1))
    m2 = max(-255, min(255, m2))
    data = [
        abs(m1), 0 if m1 >= 0 else 1,
        abs(m2), 0 if m2 >= 0 else 1,
    ]
    try:
        bus.write_i2c_block_data(MOTOR_I2C_ADDRESS, 0x00, data)
    except OSError as e:
        print(f"Motor I2C villa: {e}")


def drive(speed, offset=0):
    m1 =  (speed + offset)
    m2 = -(speed - offset)
    _send_motors(m1, m2)


def stop():
    _send_motors(0, 0)


def turn_left():
    _send_motors(-SPEED_SLOW, SPEED_SLOW)
    time.sleep(TURN_TIME)
    stop()


def turn_right():
    _send_motors(SPEED_SLOW, -SPEED_SLOW)
    time.sleep(TURN_TIME)
    stop()


def emergency_reverse():
    """Bakkar á medium speed í 2 sek, stoppar síðan."""
    print("  [EMERGENCY] Bakka!")
    _send_motors(-SPEED_MEDIUM, SPEED_MEDIUM)
    time.sleep(EMERGENCY_REVERSE_TIME)
    stop()
