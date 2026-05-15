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


def emergency_reverse(zones=None):
    """Bakkar á medium speed, snýr svo í frjálsari átt."""
    print("  [EMERGENCY] Bakka!")
    _send_motors(-SPEED_MEDIUM, SPEED_MEDIUM)
    time.sleep(EMERGENCY_REVERSE_TIME)
    stop()

    # Bera saman hliðar til að snúa í frjálsari átt
    left_vals  = []
    right_vals = []
    if zones is not None:
        left_vals  = [v for v in [zones.get('left_front'), zones.get('left_side')]  if v is not None]
        right_vals = [v for v in [zones.get('right_front'), zones.get('right_side')] if v is not None]

    left_min  = min(left_vals)  if left_vals  else 999
    right_min = min(right_vals) if right_vals else 999

    if left_min < right_min:
        print("  [EMERGENCY] Snúa hægri")
        _send_motors(SPEED_SLOW, SPEED_SLOW)
    else:
        print("  [EMERGENCY] Snúa vinstri")
        _send_motors(-SPEED_SLOW, -SPEED_SLOW)

    time.sleep(TURN_TIME * 0.6)
    stop()