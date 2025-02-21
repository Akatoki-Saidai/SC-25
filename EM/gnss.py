import time
import serial
from micropyGPS import MicropyGPS
import sc_logging
from threading import Thread

logger = sc_logging.get_logger(__name__)

class GNSS:
    def _update(self):
        while True:
            sentence = self._uart.read(self._uart.in_waiting).decode('utf-8')
            # print(sentence_all)
            # sentence_list = sentence_all.split('\n')
            # for sentence in sentence_list[-11:-2]:
            for x in sentence:
                if 10 <= ord(x) <= 126:
                    print(x)
                    stat = self._pygps.update(x)
                    if stat:
                        print(self._pygps.latitude[0],self._pygps.longitude[0] )

    def __init__(self):
        self._uart = serial.Serial('/dev/serial0', 38400, timeout = 10)
        self._pygps = MicropyGPS(9, 'dd')
        self._read_thread = Thread(target=self._update)
        self._read_thread.start()
        self._read_thread.join()
    
    # def get_forever(self, data):
    #     while True:
    #         try:
    #             sentence_all = uart.read(uart.in_waiting).decode('utf-8')
    #             sentence_list = sentence_all.split('\n')
    #             for sentence in sentence_list[-11:-2]:
    #                 for x in sentence:
    #                     if 10 <= x <= 126:
    #                         #print("5")
    #                         stat = my_gps.update(chr(x))
    #                         #print("stat:",stat,"x:",x,"chr:",chr(x))
    #                         #print(chr(x))
    #                         if stat:
    #                             #print("6")
    #                             tm = my_gps.timestamp
    #                             tm_now = (tm[0] * 3600) + (tm[1] * 60) + int(tm[2])
    #                             if (tm_now - tm_last) >= 10:
    #                                 print('=' * 20)
    #                                 print(my_gps.date_string(), tm[0], tm[1], int(tm[2]))
    #                                 print("latitude:", my_gps.latitude[0], ", longitude:", my_gps.longitude[0])


def main():
    #print("1")
    # シリアル通信設定
    uart = serial.Serial('/dev/serial0', 38400, timeout = 10)
    # gps設定
    my_gps = MicropyGPS(9, 'dd')
    #print("2")
    # 10秒ごとに表示
    tm_last = 0
    while True:
        #print("3")
        sentence_all = uart.read(uart.in_waiting).decode('utf-8')
        print("GPS data received")
        sentence_list = sentence_all.split('\n')
        #print(len(sentence))
        #continue
        for sentence in sentence_list[-11:-2]:
            #print("4")
            for x in sentence:
                if 10 <= x <= 126:
                    #print("5")
                    stat = my_gps.update(chr(x))
                    #print("stat:",stat,"x:",x,"chr:",chr(x))
                    #print(chr(x))
                    if stat:
                        #print("6")
                        tm = my_gps.timestamp
                        tm_now = (tm[0] * 3600) + (tm[1] * 60) + int(tm[2])
                        if (tm_now - tm_last) >= 10:
                            print('=' * 20)
                            print(my_gps.date_string(), tm[0], tm[1], int(tm[2]))
                            print("latitude:", my_gps.latitude[0], ", longitude:", my_gps.longitude[0])

if __name__ == "__main__":
    gnss = GNSS()
    # main()
