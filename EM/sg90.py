import time
from machine import Pin, PWM
import sc_logging

logger = sc_logging.get_logger(__name__)

class SG90:
    """
    SG90を制御するクラス

    Attributes:
        pin: GPIOのピン番号
        max_angle: 最大移動角度
        min_angle: 最小移動角度
        angle: 現在の角度
        ini_angle: 初期設定角度
        pwm: PWM制御のインスタンス
    """
    def __init__(self, pin=18, min_angle=-90, max_angle=90, ini_angle=0, freq=50) -> None:
        """
        サーボモータを制御するクラス
        """
        self._pin = pin
        self._max_angle = max_angle
        self._min_angle = min_angle
        self._angle = 0
        self._ini_angle = ini_angle
        self._freq = freq
        self._pwm = PWM(Pin(self._pin))
        self._pwm.freq(self._freq)

    def set_angle(self, target_angle: int) -> None:
        """
        サーボモータを指定した角度に設定する
        """
        try:
            if target_angle < self._min_angle or target_angle > self._max_angle:
                logger.error(f"角度は{self._min_angle}から{self._max_angle}度の間で指定してください。")
                return
            # 角度[degree] → パルス幅[μs]に変換
            pulse_width = ((target_angle + self._max_angle) / (self._max_angle - self._min_angle)) * (2000 - 1000) + 1000
            self._angle = target_angle
            # duty比（0-1023の範囲）に変換
            duty_cycle = int((pulse_width / 20000) * 1023)
            # PWM出力
            self._pwm.duty_u16(duty_cycle)
        except Exception as e:
            logger.exception()
    
    def get_angle(self):
        try:
            return self._angle
        except Exception as e:
            logger.exception()

    def set_ini_angle(self) -> None:
        """
        初期設定角度（ini_angle）に設定
        """
        try:
            self.set_angle(self._ini_angle)
        except Exception as e:
            logger.exception()

    def stop(self) -> None:
        """
        PWM信号を停止
        """
        try:
            self._pwm.duty_u16(0)
        except Exception as e:
            logger.exception()

if __name__ == "__main__":
    # 動作サンプル

    # SG90サーボモータを制御するインスタンスを作成
    sg90 = SG90(pin=18, min_angle=-90, max_angle=90, ini_angle=0, freq=50)

    # サーボ動作開始
    print(f"現在の角度: {sg90.get_angle()}")

    sg90.set_angle(10)
    # 初期位置(ini_angle)に移動
    sg90.set_ini_angle()
    time.sleep(3)
    # 現在の角度を表示
    print(f"現在の角度: {sg90.get_angle()}")
    time.sleep(3)

    # サーボ動作停止
    sg90.stop()
