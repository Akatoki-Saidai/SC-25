from gpiozero import LED
import time

LED(10).off()

try:
    print('start?')
    input()
    print('start')
    start_time = time.time()

    LED(10).on()

    input()
    LED(10).off()

    stop_time = time.time()
    
    print('stop')
    print("time: ", (stop_time - start_time), "_s")

except Exception as e:
    LED(10).off()
    pass