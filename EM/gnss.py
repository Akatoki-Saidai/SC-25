from logging import getLogger, StreamHandler  # ログを記録するため
from threading import Thread
import time

from micropyGPS import MicropyGPS
import serial

import calc_goal

class GNSS:
    def _update(self, _uart):
        while True:
            read_str = _uart.read(_uart.in_waiting).decode('utf-8')
            for read_char in read_str:
                if 10 <= ord(read_char) <= 126:
                    print(read_char, end="")
                    self._pygps.update(read_char)

    def __init__(self, gnss_uart, logger=None):
        # もしloggerが渡されなかったら，ログの記録先を標準出力に設定
        if logger is None:
            logger = getLogger(__name__)
            logger.addHandler(StreamHandler())
            logger.setLevel(10)
        self._logger = logger

        self._pygps = MicropyGPS(9, 'dd')
        self._read_thread = Thread(target=self._update, args=(gnss_uart,))
        self._read_thread.start()
    
    def get_forever(self, data):
        while True:
            try:
                if 0 < self._pygps.parsed_sentences:
                    lat = self._pygps.latitude[0]
                    lon = self._pygps.longitude[0]
                    date = self._pygps.date
                    timestamp = self._pygps
                    datetime_gnss = f"20{date[2]:02}-{date[1]:02}-{date[0]:02}T{timestamp[0]:02}:{timestamp[1]:02}:{timestamp[2]:05.2f}{self._pygps.localoffset:+02}:00"
                    self._logger.debug(f"lat: {lat}, lon: {lon}, alt: {self._pygps.altitude}, speed: {self._pygps.speed}, gnss_datetime: {datetime_gnss}")
                    data["datetime_gnss"] = datetime_gnss
                    if lat and lon:
                        data["lat"] = lat
                        data["lon"] = lon
                        calc_goal.calc_goal(data)  # ゴールまでの距離と向きを計算
            except Exception as e:
                self._logger.exception(f"An error occured in be-180 get_forever: {e}")

if __name__ == "__main__":
    try:
        gnss_uart = serial.Serial('/dev/serial0', 38400, timeout = 10)
        gnss = GNSS(gnss_uart)
        data = {"lat": None, "lon": None}
        gnss.get_forever(data)
    except KeyboardInterrupt as e:
        print(data)

    except Exception as e:
        print(f"Error in gnss: {e}")
    