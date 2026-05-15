# ── Hraðar ──────────────────────────────────────────────
SPEED_FAST   = 240
SPEED_MEDIUM = 170
SPEED_SLOW   = 100

# ── Þröskuldar (cm) ──────────────────────────────────────
THRESHOLD_FAST      = 60    # > 60cm → full speed
THRESHOLD_MEDIUM    = 20    # 30–60cm → medium
                            # < 30cm → slow + beygja
EMERGENCY_DIST      = 12    # < 12cm í framsvæði → bakka
EMERGENCY_ZONE_MIN  = 280   # emergency zone byrjar
EMERGENCY_ZONE_MAX  = 80    # emergency zone endar (fer yfir 0°)

# ── Beygju offset ────────────────────────────────────────
OFFSET_SMALL = 65
OFFSET_LARGE = 95

# ── LiDAR hólf (gráður) ──────────────────────────────────
# Beint fram
ZONE_FRONT_MIN      = 345
ZONE_FRONT_MAX      = 15

# Hægri fram
ZONE_RIGHT_FRONT_MIN = 15
ZONE_RIGHT_FRONT_MAX = 70

# Hægri hlið
ZONE_RIGHT_SIDE_MIN  = 70
ZONE_RIGHT_SIDE_MAX  = 115

# Vinstri fram
ZONE_LEFT_FRONT_MIN  = 290
ZONE_LEFT_FRONT_MAX  = 345

# Vinstri hlið
ZONE_LEFT_SIDE_MIN   = 245
ZONE_LEFT_SIDE_MAX   = 290

# ── Tímar ────────────────────────────────────────────────
EMERGENCY_REVERSE_TIME = 1.0   # sek
TURN_TIME              = 1   # sek

# ── I2C / Serial ─────────────────────────────────────────
MOTOR_I2C_ADDRESS = 0x50
LIDAR_PORT        = '/dev/ttyUSB0'
