import time
import serial
from micropyGPS import MicropyGPS
import sc_logging

logger = sc_logging.get_logger(__name__)

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
    main()
