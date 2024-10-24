from gpiozero import LED
from time import sleep

LED(17).off()

try:
    while True:
        input()
        print('start')

        LED(17).on()

        sleep(0.5)
        input()
        print('stop')
        LED(17).off()
except Exception as e:
    LED(17).off()
    pass