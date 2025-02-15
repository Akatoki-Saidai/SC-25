import pigpio
import time

# hardware PWMのchannel(同channelでは同じPWMが出力) 
# channel0: 12, 13
# channel1: 18, 19

class Motor:
    def __init__(self, pi):
        # ピン番号要確認
        self.RIGHT_MOTOR_1 = 20
        self.RIGHT_MOTOR_2 = 21
        self.LEFT_MOTOR_1 = 22
        self.LEFT_MOTOR_2 = 23

        self.MOTOR_RANGE = 100  # 0～255
        FREQUENCY = 4000  # pigpioのデフォルトサンプリングレートは5→8000,4000,2000,1600,1000,800,500,400,320のいずれか
        # duty = 0  # duty比

        self.pi = pigpio.pi()

        # 設定
        # RIGHT_MOTORピン
        self.pi.set_PWM_frequency(self.RIGHT_MOTOR_1, FREQUENCY)
        self.pi.set_PWM_range(self.RIGHT_MOTOR_1, self.MOTOR_RANGE)
        self.pi.set_PWM_frequency(self.RIGHT_MOTOR_2, FREQUENCY)
        self.pi.set_PWM_range(self.RIGHT_MOTOR_2, self.MOTOR_RANGE)
        # LEFT_MOTORピン
        self.pi.set_PWM_frequency(self.LEFT_MOTOR_1, FREQUENCY)
        self.pi.set_PWM_range(self.LEFT_MOTOR_1, self.MOTOR_RANGE)
        self.pi.set_PWM_frequency(self.LEFT_MOTOR_2, FREQUENCY)
        self.pi.set_PWM_range(self.LEFT_MOTOR_2, self.MOTOR_RANGE)


    def Speedup(self):
        # _SlowSpeedup(右の正転duty, 右の逆転duty, 左の正転duty, 左の逆転duty)
        Atode = True
        # 全部これを呼び出す

    def accel(self):
        # 正転
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, 0)

        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, 0)

    def stop(self):
        # 惰性ブレーキ
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, 0)

        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, 0)
        
    def brake(self):
        # 短絡ブレーキ
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, int(1 * self.MOTOR_RANGE))

        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, int(1 * self.MOTOR_RANGE))

    def rightturn(self):
        # 右回転(左を向く)
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, 0)

        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, 0)
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, int(1 * self.MOTOR_RANGE))
    
    
    def leftturn(self):
        # 左回転(右を向く)
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, 0)
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, int(1 * self.MOTOR_RANGE))

        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, 0)
    
    def back(self):
        # 後ろ
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, 0)
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, int(1 * self.MOTOR_RANGE))

        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, 0)
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, int(1 * self.MOTOR_RANGE))


def main():
    motor = Motor()
    motor.accel()
    motor.stop()
    motor.brake()
    motor.rightturn()
    motor.leftturn()
    motor.back()


    print("motor stop")
        
    while True:
        input()

        # 正転
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_1, int(duty * MOTOR_RANGE))
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_2, 0)
        print("motor forward")
        time.sleep(2)
        
        # 停止
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_1, 0)
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_2, 0)
        print("motor stop")
        time.sleep(2)
        
        # 逆転
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_1, 0)
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_2, int(duty * MOTOR_RANGE))
        print("motor reverse")
        time.sleep(2)

        # 停止
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_1, 0)
        motor_pi.set_PWM_dutycycle(RIGHT_MOTOR_2, 0)
        print("motor stop")
        time.sleep(3)

        # pi.stop()
    

if __name__ == '__main__':
    main()
