import pigpio
import time

# hardware PWMのchannel(同channelでは同じPWMが出力) 
# channel0: 12, 13
# channel1: 18, 19

def main():
    RIGHT_MOTOR_1 = 20
    RIGHT_MOTOR_2 = 21
    MOTOR_RANGE = 100  # 0～255
    FREQUENCY = 4000  # pigpioのデフォルトサンプリングレートは5なので8000,4000,2000,1600,1000,800,500,400,320のいずれか
    duty = 0.5  # duty比

    pi = pigpio.pi()

    # 設定
    # RIGHT_MOTORピン
    pi.set_PWM_frequency(RIGHT_MOTOR_1, FREQUENCY)
    pi.set_PWM_range(RIGHT_MOTOR_1, MOTOR_RANGE)
    # LEFT_MOTORピン
    pi.set_PWM_frequency(RIGHT_MOTOR_2, FREQUENCY)
    pi.set_PWM_range(RIGHT_MOTOR_2, MOTOR_RANGE)
        
    while True:
        # 正転
        pi.set_PWM_dutycycle(RIGHT_MOTOR_1, int(duty * MOTOR_RANGE))
        pi.set_PWM_dutycycle(RIGHT_MOTOR_2, 0)
        print("motor forward")
        time.sleep(2)
        
        # 停止
        pi.set_PWM_dutycycle(RIGHT_MOTOR_1, 0)
        pi.set_PWM_dutycycle(RIGHT_MOTOR_2, 0)
        print("motor stop")
        time.sleep(2)
        
        # 逆転
        pi.set_PWM_dutycycle(RIGHT_MOTOR_1, 0)
        pi.set_PWM_dutycycle(RIGHT_MOTOR_2, int(duty * MOTOR_RANGE))
        print("motor reverse")
        time.sleep(2)

        # 停止
        pi.set_PWM_dutycycle(RIGHT_MOTOR_1, 0)
        pi.set_PWM_dutycycle(RIGHT_MOTOR_2, 0)
        print("motor stop")
        time.sleep(3)

        # pi.stop()
    

if __name__ == '__main__':
    main()
