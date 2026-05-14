import time
import random
import pygame
pygame.mixer.init()
sound1 = pygame.mixer.Sound('/home/skitamixvol3/Downloads/Rammstein-Du hast .mp3')

from constants import (
    SPEED_FAST, SPEED_SLOW,
    OFFSET_LARGE,
    EMERGENCY_DIST,
)
from sensor import get_scan, stop_lidar
from motor  import drive, stop, emergency_reverse

import lcd_display as lcd
from lcd_display import determine_direction

# ── Þröskuldar fyrir smooth logic ──────────────────────────
REACT_DIST = 80   # cm - byrjar að bregðast við (hægja, beyja)
STOP_DIST  = 15   # cm - lágmarkshraði (rétt fyrir ofan emergency)


def compute_drive(zones):
    """
    Reiknar speed og offset út frá öllum zones í einu.
    Skilar (speed, offset).

    Speed:  línuleg interpolation milli SPEED_FAST og SPEED_SLOW
            út frá næsta hlut í framsvæði.
            Hliðar hafa hálft vægi svo við stoppa ekki vegna veggs.

    Offset: línuleg interpolation milli 0 og OFFSET_LARGE
            út frá mismun vinstri/hægri nálægðar.
            Því meiri munur, því stærri beygja.
    """
    front       = zones['front']
    left_front  = zones['left_front']
    right_front = zones['right_front']
    left_side   = zones['left_side']
    right_side  = zones['right_side']

    # ── 1. Hraðaútreikningur ──────────────────────────────────
    # Framhlutarar hafa fulla áhrif, hliðar helmings (við viljum ekki stoppa vegna veggjar)
    forward_vals = [v for v in [front, left_front, right_front] if v is not None]
    side_vals    = [v * 2 for v in [left_side, right_side] if v is not None]  # *2 = helmings áhrif

    all_vals = forward_vals + side_vals
    closest  = min(all_vals) if all_vals else 999

    # Línuleg interpolation: STOP_DIST → SPEED_SLOW, REACT_DIST → SPEED_FAST
    t     = (closest - STOP_DIST) / (REACT_DIST - STOP_DIST)
    t     = max(0.0, min(1.0, t))
    speed = int(SPEED_SLOW + t * (SPEED_FAST - SPEED_SLOW))

    # ── 2. Offset útreikningur ────────────────────────────────
    left_vals_  = [v for v in [left_front, left_side]  if v is not None]
    right_vals_ = [v for v in [right_front, right_side] if v is not None]

    left_min  = min(left_vals_)  if left_vals_  else 999
    right_min = min(right_vals_) if right_vals_ else 999

    # diff > 0 → hægri nær → beyja vinstri (offset jákvætt)
    # diff < 0 → vinstri nær → beyja hægri (offset neikvætt)
    diff  = right_min - left_min
    ratio = max(-1.0, min(1.0, diff / 40.0))  # 40cm = full offset
    offset = int(ratio * OFFSET_LARGE)

    # Hlutur beint fram, engar hliðarupplýsingar → velja handahófskennt
    if left_min == 999 and right_min == 999 and front is not None and front < REACT_DIST:
        offset = OFFSET_LARGE if random.random() < 0.5 else -OFFSET_LARGE

    return speed, offset


def main():
    print("═" * 40)
    print("  HVR1013 Robot - RPLiDAR S2")
    print("═" * 40)
    time.sleep(1)
    sound1.play()
    lcd.start_display()

    try:
        while True:
            zones = get_scan()
            emg   = zones['emergency']

            direction, distance = determine_direction(zones)
            lcd.set_direction(direction, distance)
            cpu_temp = lcd.get_cpu_temp()

            speed, offset = compute_drive(zones)

            print(
                f"CPU:{cpu_temp:.0f}C | Dir:{direction} | Dist:{distance:.0f}cm | "
                f"spd={speed} off={offset} | "
                f"F={zones['front']} LF={zones['left_front']} RF={zones['right_front']} "
                f"LS={zones['left_side']} RS={zones['right_side']} EMG={emg}"
            )

            # Emergency - bakka og snúa
            if emg is not None and emg < EMERGENCY_DIST:
                emergency_reverse(zones)
                continue

            drive(speed, offset)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStoppar...")
        stop()
        stop_lidar()


if __name__ == "__main__":
    main()

    #gaygay