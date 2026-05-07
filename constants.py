# ── Hraðar ──────────────────────────────────────────────
SPEED_FAST   = 200
SPEED_MEDIUM = 170
SPEED_SLOW   = 80

# ── Þröskuldar (cm) ──────────────────────────────────────
THRESHOLD_FAST      = 60    # > 60cm → full speed
THRESHOLD_MEDIUM    = 30    # 30–60cm → medium
                            # < 30cm → slow + beygja
EMERGENCY_DIST      = 12    # < 12cm í framsvæði → bakka
EMERGENCY_ZONE_MIN  = 280   # emergency zone byrjar
EMERGENCY_ZONE_MAX  = 80    # emergency zone endar (fer yfir 0°)

# ── Beygju offset ────────────────────────────────────────
OFFSET_SMALL = 40
OFFSET_LARGE = 90

# ── LiDAR hólf (gráður) ──────────────────────────────────
# Beint fram
ZONE_FRONT_MIN      = 345
ZONE_FRONT_MAX      = 15

# Hægri fram
ZONE_RIGHT_FRONT_MIN = 15
ZONE_RIGHT_FRONT_MAX = 70

# Hægri hlið
ZONE_RIGHT_SIDE_MIN  = 70
ZONE_RIGHT_SIDE_MAX  = 130

# Vinstri fram
ZONE_LEFT_FRONT_MIN  = 290
ZONE_LEFT_FRONT_MAX  = 345

# Vinstri hlið
ZONE_LEFT_SIDE_MIN   = 230
ZONE_LEFT_SIDE_MAX   = 290

# ── Tímar ────────────────────────────────────────────────
EMERGENCY_REVERSE_TIME = 2.0   # sek
TURN_TIME              = 0.8   # sek

# ── I2C / Serial ─────────────────────────────────────────
MOTOR_I2C_ADDRESS = 0x50
LIDAR_PORT        = '/dev/ttyUSB0'
