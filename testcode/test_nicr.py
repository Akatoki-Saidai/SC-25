from gpiozero import LED
import time

LED(17).off()

try:
    print('start?')
    input()
    print('start')
    start_time = time.time()

    LED(17).on()

    input()
    LED(17).off()

    stop_time = time.time()
    
    print('stop')
    print("time: ", (stop_time - start_time), "_s")

except Exception as e:
    LED(17).off()
    pass