from gpiozero import PWMLED
from time import sleep

PWMLED(4).value = 0
PWMLED(23).value = 0
PWMLED(13).value = 0
PWMLED(5).value = 0

try:
    while True:
        input()
        print('start')

        PWMLED(4).value = 1
        PWMLED(23).value = 0
        PWMLED(13).value = 1
        PWMLED(5).value = 0

        sleep(0.5)
        input()
        print('stop')
        PWMLED(4).value = 0
        PWMLED(23).value = 0
        PWMLED(13).value = 0
        PWMLED(5).value = 0
except Exception as e:
    PWMLED(4).value = 0
    PWMLED(23).value = 0
    PWMLED(13).value = 0
    PWMLED(5).value = 0

