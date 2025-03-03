from gpiozero import LED
import time

NiCr_PIN = LED(10)
NiCr_PIN.off()

try:
    print('start?')
    input()
    print('start')
    start_time = time.time()

    NiCr_PIN.on()

    input()
    NiCr_PIN.off()

    stop_time = time.time()
    
    print('stop')
    print("time: ", (stop_time - start_time), "_s")

except Exception as e:
    NiCr_PIN.off()
    pass