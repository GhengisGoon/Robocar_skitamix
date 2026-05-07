import time
import threading
from rplidar import RPLidar
from constants import (
    LIDAR_PORT,
    ZONE_FRONT_MIN, ZONE_FRONT_MAX,
    ZONE_RIGHT_FRONT_MIN, ZONE_RIGHT_FRONT_MAX,
    ZONE_RIGHT_SIDE_MIN, ZONE_RIGHT_SIDE_MAX,
    ZONE_LEFT_FRONT_MIN, ZONE_LEFT_FRONT_MAX,
    ZONE_LEFT_SIDE_MIN, ZONE_LEFT_SIDE_MAX,
    EMERGENCY_ZONE_MIN, EMERGENCY_ZONE_MAX,
)

lidar = RPLidar(LIDAR_PORT, baudrate=1000000, timeout=3)
lidar.start_motor()
time.sleep(2)  # bíða eftir að mótor nái hraða

_latest_scan = []
_scan_lock   = threading.Lock()
_running     = True


def _background_scan():
    """Keyrir í bakgrunni, restartast sjálfkrafa við villu."""
    global _latest_scan, _running
    print("[LiDAR thread] byrjar")
    while _running:
        try:
            for scan in lidar.iter_scans(max_buf_meas=2000):
                if not _running:
                    break
                with _scan_lock:
                    _latest_scan = scan
        except Exception as e:
            print(f"[LiDAR villa, reyni aftur]: {e}")
            time.sleep(0.5)
    print("[LiDAR thread] hætti")


_thread = threading.Thread(target=_background_scan, daemon=True)
_thread.start()
time.sleep(2)  # bíða eftir fyrsta scan


def stop_lidar():
    global _running
    _running = False
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()


def _in_zone(angle, zone_min, zone_max):
    """Athugar hvort gráða sé innan hólfs, tekur tillit til wrap-around yfir 0°."""
    if zone_min > zone_max:  # wrap-around (t.d. 345°–15°)
        return angle >= zone_min or angle <= zone_max
    return zone_min <= angle <= zone_max


def get_scan():
    """
    Les nýjasta scan úr bakgrunn thread.
    Skilar dict með lágmarks-fjarlægð (cm) í hverju hólfi.
    None ef ekkert mælst í hólfi.
    """
    with _scan_lock:
        scan = list(_latest_scan)

    zones = {
        'front':       [],
        'right_front': [],
        'right_side':  [],
        'left_front':  [],
        'left_side':   [],
        'emergency':   [],
    }

    for (_, angle, distance) in scan:
        d = distance / 10  # mm → cm
        if d < 6:           # undir 6cm = noise
            continue

        # Emergency zone (280°–80°, fer yfir 0°)
        if _in_zone(angle, EMERGENCY_ZONE_MIN, EMERGENCY_ZONE_MAX):
            zones['emergency'].append(d)

        # Hólf - ekki elif þar sem emergency er aðskilið
        if _in_zone(angle, ZONE_FRONT_MIN, ZONE_FRONT_MAX):
            zones['front'].append(d)
        elif _in_zone(angle, ZONE_RIGHT_FRONT_MIN, ZONE_RIGHT_FRONT_MAX):
            zones['right_front'].append(d)
        elif _in_zone(angle, ZONE_RIGHT_SIDE_MIN, ZONE_RIGHT_SIDE_MAX):
            zones['right_side'].append(d)
        elif _in_zone(angle, ZONE_LEFT_FRONT_MIN, ZONE_LEFT_FRONT_MAX):
            zones['left_front'].append(d)
        elif _in_zone(angle, ZONE_LEFT_SIDE_MIN, ZONE_LEFT_SIDE_MAX):
            zones['left_side'].append(d)

    return {
        key: round(min(vals), 1) if vals else None
        for key, vals in zones.items()
    }
