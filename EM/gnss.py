import time
import serial
from logging import getLogger, StreamHandler  # ログを記録するため
from micropyGPS import MicropyGPS
from threading import Thread

class GNSS:
    def _update(self):
        while True:
            read_str = self._uart.read(self._uart.in_waiting).decode('utf-8')
            for read_char in read_str:
                if 10 <= ord(read_char) <= 126:
                    print(read_char, end="")
                    self._pygps.update(read_char)

    def __init__(self, logger=None):
        # もしloggerが渡されなかったら，ログの記録先を標準出力に設定
        if logger is None:
            logger = getLogger(__name__)
            logger.addHandler(StreamHandler())
            logger.setLevel(10)
        self._logger = logger

        self._uart = serial.Serial('/dev/serial0', 38400, timeout = 10)
        self._pygps = MicropyGPS(9, 'dd')
        self._read_thread = Thread(target=self._update)
        self._read_thread.start()
    
    def get_forever(self, data):
        while True:
            try:
                if 0 < self._pygps.parsed_sentences:
                    lat = self._pygps.latitude[0]
                    lon = self._pygps.longitude[0]
                    self._logger.debug(f"lat: {lat}, lon: {lon}, alt: {self._pygps.altitude}, speed: {self._pygps.speed}, date: {self._pygps.date}, time: {self._pygps.timestamp}")
                    if lat and lon:
                        data["lat"] = lat
                        data["lon"] = lon
            except Exception as e:
                self._logger.exception("An error occured!")

if __name__ == "__main__":
    gnss = GNSS()
    data = {"lat": None, "lon": None}
    gnss.get_forever(data)