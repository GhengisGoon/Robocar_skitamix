import time
import pygame
pygame.mixer.init()  # Initialize the mixer module.
sound1 = pygame.mixer.Sound('/home/skitamixvol3/Downloads/Rammstein-Du hast .mp3')  # Load a sound.
from constants import (
    THRESHOLD_FAST, THRESHOLD_MEDIUM,
    SPEED_FAST, SPEED_MEDIUM, SPEED_SLOW,
    OFFSET_SMALL, OFFSET_LARGE,
    EMERGENCY_DIST,
)
from sensor import get_scan, stop_lidar
from motor  import drive, stop, emergency_reverse

import lcd_display as lcd
from lcd_display import determine_direction

def choose_offset(zones, speed_level):
    """
    Reiknar beygju-offset út frá hólfum.
    offset > 0 → vinstri motor hraðar → beygja hægri
    offset < 0 → hægri motor hraðar  → beygja vinstri
    """
    offset_val = OFFSET_LARGE if speed_level == 'slow' else OFFSET_SMALL

    left_side  = zones['left_side']
    right_side = zones['right_side']
    left_front = zones['left_front']
    right_front = zones['right_front']

    # Hliðar hafa forgang - ef ein hlið er lokuð, beygja í burtu
    left_blocked  = left_side  is not None and left_side  < THRESHOLD_MEDIUM
    right_blocked = right_side is not None and right_side < THRESHOLD_MEDIUM

    if left_blocked and not right_blocked:
        return -offset_val    # vinstri lokuð → beygja hægri
    if right_blocked and not left_blocked:
        return offset_val   # hægri lokuð  → beygja vinstri

    # Nota fram-hólf - beygja í átt að frjálsara svæði
    lf = left_front  if left_front  is not None else 999
    rf = right_front if right_front is not None else 999

    if lf > rf:
        return offset_val   # vinstri frjálsara → beygja vinstri
    if rf > lf:
        return -offset_val    # hægri frjálsara  → beygja hægri
    return 0


def main():
    print("═" * 40)
    print("  HVR1013 Robot - RPLiDAR S2")
    print("═" * 40)
    time.sleep(1)
    sound1.play()  # Play the sound.
    # Start LCD display
    lcd.start_display()


    try:
        while True:
           
            zones = get_scan()
            front = zones['front']
            emg   = zones['emergency']

            # Determine direction for LCD
            direction, distance = determine_direction(zones)
            
            # Update LCD display
            lcd.set_direction(direction, distance)
            
            # Get CPU temperature (optional - for console output)
            cpu_temp = lcd.get_cpu_temp()

            print(
                f"CPU:{cpu_temp:.0f}C | Dir:{direction} | Dist:{distance:.0f}cm | "
                f"F={front} LF={zones['left_front']} RF={zones['right_front']} "
                f"LS={zones['left_side']} RS={zones['right_side']} EMG={emg}"
            )

            #  1. Emergency - eitthvað < 12cm í 280°–80°
            if emg is not None and emg < EMERGENCY_DIST:
                emergency_reverse()
                continue

            #  2. Hindrun nálægt beint fram → hægt + stór beygja
            if front is not None and front < THRESHOLD_MEDIUM:
                offset = choose_offset(zones, 'slow')
                drive(SPEED_SLOW, offset)

            #  3. Hindrun í miðlungs fjarlægð → miðlungs + lítil beygja
            elif front is not None and front < THRESHOLD_FAST:
                offset = choose_offset(zones, 'medium')
                drive(SPEED_MEDIUM, offset)

           
            #  4. Frjálst → fullur hraði beint áfram 
            else:
                drive(SPEED_FAST)

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStoppar...")
        stop()
        stop_lidar()


if __name__ == "__main__":
    main()

    #gaygay
