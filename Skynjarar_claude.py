
import smbus2
import time
from collections import deque

class SRF02:
    CMD_RANGE_CM = 0x51
    CMD_RANGE_INCH = 0x50
    REG_CMD = 0x00
    REG_HIGH = 0x02
    REG_LOW = 0x03
    MEASURE_TIME = 0.07  # 70ms - minimum mælitími SRF02

    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self._history = deque(maxlen=5)

    def _read_distance(self):
        try:
            self.bus.write_byte_data(self.address, self.REG_CMD, self.CMD_RANGE_CM)
            time.sleep(self.MEASURE_TIME)
            high = self.bus.read_byte_data(self.address, self.REG_HIGH)
            low = self.bus.read_byte_data(self.address, self.REG_LOW)
            return (high << 8) | low
        except OSError:
            return None

    def get_distance(self):
        """Skilar meðaltal af 3 mælingum fyrir nákvæmni"""
        readings = []
        for _ in range(3):
            d = self._read_distance()
            if d is not None and 15 <= d <= 600:  # SRF02 range: 15cm - 6m
                readings.append(d)
        if not readings:
            return None
        avg = sum(readings) / len(readings)
        self._history.append(avg)
        return round(avg, 1)

    def get_smoothed(self):
        """Skilar smoothed gildi úr history"""
        if not self._history:
            return None
        return round(sum(self._history) / len(self._history), 1)


def main():
    bus = smbus2.SMBus(1)
    
    sensor1 = SRF02(bus, 0x70)
    sensor2 = SRF02(bus, 0x71)

    print("SRF02 Dual Sensor - Mælingar í gangi")
    print("=" * 45)
    print(f"{'Tími':>10} | {'Sensor 1 (cm)':>13} | {'Sensor 2 (cm)':>13}")
    print("-" * 45)

    try:
        while True:
            t = time.strftime("%H:%M:%S")
            d1 = sensor1.get_distance()
            d2 = sensor2.get_distance()

            s1 = f"{d1:>10.1f} cm" if d1 else "     villa    "
            s2 = f"{d2:>10.1f} cm" if d2 else "     villa    "

            print(f"{t:>10} | {s1:>13} | {s2:>13}")
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nHætt!")
        bus.close()

if __name__ == "__main__":
    main()
