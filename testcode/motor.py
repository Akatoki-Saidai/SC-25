import pigpio
import time

# hardware PWMのchannel(同channelでは同じPWMが出力) 
# channel0: 12, 13
# channel1: 18, 19

class Motor(object):
    def __init__(self, right_pin1=20, right_pin2=21, left_pin1=5, left_pin2=7):
        # ピン番号要確認
        self.RIGHT_MOTOR_1 = right_pin1
        self.RIGHT_MOTOR_2 = right_pin2
        self.LEFT_MOTOR_1 = left_pin1
        self.LEFT_MOTOR_2 = left_pin2

        self.MOTOR_RANGE = 100  # 0～255
        FREQUENCY = 4000  # pigpioのデフォルトサンプリングレートは5→8000,4000,2000,1600,1000,800,500,400,320のいずれか
        # duty = 0  # duty比

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon in motor")

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

        # 初期化
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, 0)
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, 0)
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, 0)
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, 0)


    def Speedup(self, right_pin1_duty, right_pin2_duty, left_pin1_duty, left_pin2_duty):
        # Speedup(右の正転duty, 右の逆転duty, 左の正転duty, 左の逆転duty)
        # 全部これを呼び出す

        # メモ：
        # getにしてそこからアクセルとブレーキ分岐
        # 今より大きければアクセル，小さければブレーキ
        # 小さければマイナスを足す　新-今
        # どちらも0以上になってはならない(どちらかは必ず0)
        # 0でない方に足し続ける
        delta_duty = 0.20

        right_pin1_duty_now = self.pi.get_PWM_dutycycle(self.RIGHT_MOTOR_1)
        right_pin2_duty_now = self.pi.get_PWM_dutycycle(self.RIGHT_MOTOR_2)
        left_pin1_duty_now = self.pi.get_PWM_dutycycle(self.LEFT_MOTOR_1)
        left_pin2_duty_now = self.pi.get_PWM_dutycycle(self.LEFT_MOTOR_2)
    

        if (right_pin1_duty > 0) and (right_pin2_duty > 0):
            print("Right: Both pin1 and pin2 over 0 voltage")
            return
        elif (left_pin1_duty > 0) and (left_pin2_duty > 0):
            print("Left: Both pin1 and pin2 over 0 voltage")
            return
        
        # 入力と現行の+-が違ったら現行側を0に直す
        # 右が反転していた場合
        if abs(right_pin1_duty - right_pin1_duty_now) + abs(right_pin2_duty - right_pin2_duty_now) > 1:
            if right_pin1_duty_now > right_pin2_duty_now:
                # right_inverse_duty = right_pin1_duty
                right_inverse_duty_now = right_pin1_duty_now
                right_inverse_pin = self.RIGHT_MOTOR_1
            elif right_pin2_duty_now > right_pin1_duty_now:
                # right_inverse_duty = right_pin2_duty
                right_inverse_duty_now = right_pin2_duty_now
                right_inverse_pin = self.RIGHT_MOTOR_2
            else:
                print("right duty +- is different. But right motor already stopped")

            if left_pin1_duty_now > left_pin2_duty_now:
                # left_inverse_duty = left_pin1_duty
                left_inverse_duty_now = left_pin1_duty_now
                left_inverse_pin = self.LEFT_MOTOR_1
            elif left_pin2_duty_now > left_pin1_duty_now:
                # left_inverse_duty = left_pin2_duty
                left_inverse_duty_now = left_pin2_duty_now
                left_inverse_pin = self.LEFT_MOTOR_2
            else:
                print("left duty +- is different. But left motor already stopped")

            for i in range(int(1 / delta_duty)):
                if 0 <= right_inverse_duty_now <= 1:
                    self.pi.set_PWM_dutycycle(right_inverse_pin, int(right_inverse_duty_now * self.MOTOR_RANGE))
                    right_inverse_duty_now -= delta_duty
                else:
                    pass
                if 0 <= left_inverse_duty_now <=1:
                    self.pi.set_PWM_dutycycle(left_inverse_pin, int(left_inverse_duty_now * self.MOTOR_RANGE))
                    left_inverse_duty_now -= delta_duty
                else:
                    pass

                time.sleep(0.1)

            self.pi.set_PWM_dutycycle(right_inverse_pin, 0)
            self.pi.set_PWM_dutycycle(left_inverse_pin, 0)
                    

        # 全てのピンは現在0(の予定)
        if right_pin1_duty > right_pin2_duty:
            right_inverse_duty = right_pin1_duty
            right_inverse_pin = self.RIGHT_MOTOR_1
        elif right_pin2_duty> right_pin1_duty:
            right_inverse_duty = right_pin2_duty
            right_inverse_pin = self.RIGHT_MOTOR_2
        else:
            right_inverse_duty = 0
            print("Right pin is already 0")
        right_inverse_duty_now = 0

        if left_pin1_duty > left_pin2_duty:
            left_inverse_duty = left_pin1_duty
            # left_inverse_duty_now = left_pin1_duty_now
            left_inverse_pin = self.LEFT_MOTOR_1
        elif left_pin2_duty > left_pin1_duty:
            left_inverse_duty = left_pin2_duty
            # left_inverse_duty_now = left_pin2_duty_now
            left_inverse_pin = self.LEFT_MOTOR_2
        else:
            left_inverse_duty = 0
            print("Left pin is already 0")
        left_inverse_duty_now = 0

        for i in range(int(1 / delta_duty)):
            if 0 <= right_inverse_duty_now <= right_inverse_duty:
                self.pi.set_PWM_dutycycle(right_inverse_pin, int(right_inverse_duty_now * self.MOTOR_RANGE))
                right_inverse_duty_now += delta_duty
            else:
                pass
            if 0 <= left_inverse_duty_now <= left_inverse_duty:
                self.pi.set_PWM_dutycycle(left_inverse_pin, int(left_inverse_duty_now * self.MOTOR_RANGE))
                left_inverse_duty_now += delta_duty
            else:
                pass

                time.sleep(0.1)
                
        self.pi.set_PWM_dutycycle(right_inverse_pin, right_inverse_duty)
        self.pi.set_PWM_dutycycle(left_inverse_pin, left_inverse_duty)


    def accel(self):
        # 正転
        self.Speedup(1, 0, 1, 0)

    def stop(self):
        # 惰性ブレーキ
        self.Speedup(0, 0, 0, 0)
        
    def brake(self):
        # 短絡ブレーキ(モーターには負荷)
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.RIGHT_MOTOR_2, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_1, int(1 * self.MOTOR_RANGE))
        self.pi.set_PWM_dutycycle(self.LEFT_MOTOR_2, int(1 * self.MOTOR_RANGE))

    def rightturn(self):
        # 右回転(左を向く)
        self.Speedup(1, 0, 0, 1)
    
    def leftturn(self):
        # 左回転(右を向く)
        self.Speedup(0, 1, 1, 0)
    
    def back(self):
        # 後ろ
        self.Speedup(0, 1, 0, 1)


def main():
    motor = Motor()
    print("motor initialized\nstart?")
    input()

    motor.accel()
    time.sleep(2)
    motor.stop()
    time.sleep(1)

    motor.rightturn()
    time.sleep(2)
    motor.leftturn()
    time.sleep(2)
    motor.stop()
    time.sleep(1)

    motor.accel()
    time.sleep(2)
    motor.brake()
    time.sleep(2)
    
    motor.back()
    time.sleep(2)
    motor.stop()
    print("motor stop")
    time.sleep(1)
        
    '''
    while True:
        input()

        motor.accel()
        motor.stop()
        motor.rightturn()
        motor.stop()
        motor.leftturn()
        motor.stop()
    '''


if __name__ == '__main__':
    main()
