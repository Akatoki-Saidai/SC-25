import pigpio
import time
from logging import getLogger, StreamHandler  # ログを記録するため

class MotorChannel(object):
    # 1つのモーターの制御クラス
    # inverseとreverseどちらか一方のピンにのみPWM出力を行う
    
    def __init__(self, pi, pin1, pin2, logger=None):
        # もしloggerが渡されなかったら，ログの記録先を標準出力に設定
        if logger is None:
            logger = getLogger(__name__)
            logger.addHandler(StreamHandler())
            logger.setLevel(10)
        self._logger = logger

        self.pi = pi
        self.pin_inverse = pin1
        self.pin_reverse = pin2
        self.MOTOR_RANGE = 100  # 0～255の範囲で設定
        self.FREQUENCY = 4000  # pigpioのデフォルトサンプリングレートは5→8000,4000,2000,1600,1000,800,500,400,320のいずれか
        self.delta_duty = 0.1
        self.delta_time = 0.05

        # PWM設定
        self.pi.set_PWM_frequency(self.pin_inverse, self.FREQUENCY)
        self.pi.set_PWM_range(self.pin_inverse, self.MOTOR_RANGE)

        self.pi.set_PWM_frequency(self.pin_reverse, self.FREQUENCY)
        self.pi.set_PWM_range(self.pin_reverse, self.MOTOR_RANGE)

        # 初期状態は停止
        self.current_duty = 0.0   # 0～1の割合
        self.current_direction = 0  # 1: 正転, -1: 逆転, 0: 停止
        self._apply_duty()
    
    def __del__(self):
        # オブジェクトの削除時のクリーンアップ
        if self.pi.connected:
            self._pi.set_mode(self.pin_inverse, pigpio.INPUT)
            self._pi.set_mode(self.pin_reverse, pigpio.INPUT)
            # self._pi.stop()

    def _apply_duty(self):
        # PWM出力を更新(片側)

        if self.current_direction == 1:
            # 正転：inverseに duty、reverseは0
            self.pi.set_PWM_dutycycle(self.pin_inverse, int(self.current_duty * self.MOTOR_RANGE))
            self.pi.set_PWM_dutycycle(self.pin_reverse, 0)
        elif self.current_direction == -1:
            # 逆転：reverseに duty、inverseは0
            self.pi.set_PWM_dutycycle(self.pin_inverse, 0)
            self.pi.set_PWM_dutycycle(self.pin_reverse, int(self.current_duty * self.MOTOR_RANGE))
        else:
            # 停止
            self.pi.set_PWM_dutycycle(self.pin_inverse, 0)
            self.pi.set_PWM_dutycycle(self.pin_reverse, 0)

    def update(self, target_inverse, target_reverse):
        try:
            # duty を漸進的に更新
            # target_inverse, target_reverse は [0,1]の値。両方同時に0より大きい場合はエラー
            
            if target_inverse > 0 and target_reverse > 0:
                self._logger.error(f"pin1:{self.pin_inverse}, pin2:{self.pin_reverse}: Both pin over 0 voltage")
                raise ValueError(f"pin1:{self.pin_inverse}, pin2:{self.pin_reverse}: Both pin over 0 voltage")
            
            if target_inverse > 0:
                target_direction = 1
                target_duty = target_inverse
            elif target_reverse > 0:
                target_direction = -1
                target_duty = target_reverse
            else:
                target_direction = 0
                target_duty = 0.0

            # 入力と現行の+-が違ったら現行側を0に直す
            if self.current_direction != target_direction:
                while self.current_duty > 0:
                    self.current_duty = max(self.current_duty - self.delta_duty, 0)
                    self._apply_duty()
                    time.sleep(self.delta_time)
                self.current_direction = target_direction

            # 全てのピンは現在0(の予定)
            # 現在の duty から目標 duty へ漸進的に変化
            if target_duty > self.current_duty:
                # 加速
                while self.current_duty < target_duty:
                    self.current_duty = min(self.current_duty + self.delta_duty, target_duty)
                    self._apply_duty()
                    time.sleep(self.delta_time)
            elif target_duty < self.current_duty:
                # 減速
                while self.current_duty > target_duty:
                    self.current_duty = max(self.current_duty - self.delta_duty, target_duty)
                    self._apply_duty()
                    time.sleep(self.delta_time)
        except Exception as e:
            self._logger.exception("An error occured!")

class Motor(object):
    # 各モーターはMotorChannelで管理
    
    def __init__(self, right_pin1=20, right_pin2=21, left_pin1=5, left_pin2=7):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            self._logger.error("Failed to connect to pigpio daemon in motor")
            raise RuntimeError("Failed to connect to pigpio daemon in motor")
        
        self.right_motor = MotorChannel(self.pi, right_pin1, right_pin2)
        self.left_motor  = MotorChannel(self.pi, left_pin1, left_pin2)

    def accel(self):
        # 正転
        try:
            self.right_motor.update(1, 0)
            self.left_motor.update(1, 0)
        except Exception as e:
            self._logger.exception("An error occured!")

    def stop(self):
        # 惰性ブレーキ
        try:
            self.right_motor.update(0, 0)
            self.left_motor.update(0, 0)
        except Exception as e:
            self._logger.exception("An error occured!")

    def brake(self):
        # 短絡ブレーキ(モーターには負荷)
        try:
            self.pi.set_PWM_dutycycle(self.right_motor.pin_inverse, int(1 * self.right_motor.MOTOR_RANGE))
            self.pi.set_PWM_dutycycle(self.right_motor.pin_reverse, int(1 * self.right_motor.MOTOR_RANGE))
            self.pi.set_PWM_dutycycle(self.left_motor.pin_inverse, int(1 * self.left_motor.MOTOR_RANGE))
            self.pi.set_PWM_dutycycle(self.left_motor.pin_reverse, int(1 * self.left_motor.MOTOR_RANGE))

            # 状態更新
            self.right_motor.current_duty = 0
            self.right_motor.current_direction = 0
            self.left_motor.current_duty = 0
            self.left_motor.current_direction = 0
        except Exception as e:
            self._logger.exception("An error occured!")

    def leftturn(self):
        # 左回転(右を向く)
        try:
            self.right_motor.update(0, 1)
            self.left_motor.update(1, 0)
        except Exception as e:
            self._logger.exception("An error occured!")

    def rightturn(self):
        # 右回転(左を向く)
        try:
            self.right_motor.update(1, 0)
            self.left_motor.update(0, 1)
        except Exception as e:
            self._logger.exception("An error occured!")

    def back(self):
        # 後ろ
        try:
            self.right_motor.update(0, 1)
            self.left_motor.update(0, 1)
        except Exception as e:
            self._logger.exception("An error occured!")

    def cleanup(self):
        try:
            self.pi.stop()
        except Exception as e:
            self._logger.exception("An error occured!")

def main():
    motor = Motor(right_pin1=20, right_pin2=21, left_pin1=5, left_pin2=7)
    print("motor initialized\nstart?")
    input()

    print("accel")
    motor.accel()
    time.sleep(2)

    print("stop")
    motor.stop()
    time.sleep(1)

    print("rightturn")
    motor.rightturn()
    time.sleep(2)

    print("leftturn")
    motor.leftturn()
    time.sleep(2)

    print("stop")
    motor.stop()
    time.sleep(1)

    print("accel")
    motor.accel()
    time.sleep(2)

    print("brake")
    motor.brake()
    time.sleep(2)

    print("back")
    motor.back()
    time.sleep(2)

    print("stop")
    motor.stop()
    time.sleep(1)
    
    print("test movement end")
    motor.cleanup()

if __name__ == '__main__':
    main()
