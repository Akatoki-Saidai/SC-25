import pigpio
import time


"""
参考にしたサイト
コード全体：https://qiita.com/Marusankaku_E/items/7cc1338fbab04291a296
SG90のデータシート：https://akizukidenshi.com/goodsaffix/SG90_a.pdf
S35 STDの仕様について：https://qiita.com/yukima77/items/cb640ce99c9fd624a308
上同：https://akizukidenshi.com/catalog/g/g108305/
"""



class SG90:
    """
    SG90を制御するクラス

    Attributes:
        pin: GPIOのピン番号
        max_angle: 最大移動角度
        min_angle: 最小移動角度
        angle: 現在の角度
        ini_angle: 初期設定角度
        pi: gpio制御
    """
    def __init__(self, pin=17, min_angle=-90, max_angle=90, ini_angle=0,freq=50) -> None:
        """
        サーボモータを制御するクラス
        """
        self.pin = pin
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.angle = 0
        self.ini_angle = ini_angle
        self.pi = None
        self.freq = freq

    def start(self) -> None:
        """
        GPIOの開始処理
        """
        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

    def stop(self) -> None:
        """
        GPIOの終了処理
        """
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.stop()

    # def set_angle(self, target_angle: int) -> None:
    #     """
    #     サーボモータを指定角度に移動する

    #     Args:
    #         target_angle (int): 動作させる角度
    #     """
    #     if target_angle < self.min_angle or target_angle > self.max_angle:
    #         print(f"角度は{self.min_angle}から{self.max_angle}度の間で指定してください。")
    #         return

    #     # 角度を0.5から2500のパルス幅にマッピングする(SG90の仕様に合わせたつもりだが,pulse_widthの仕様が不明なためちょっと怪しい.引数の単位が謎なんよな．今はμs pulse)
    #     pulse_width = ((target_angle+90) / 180) * (2400 - 500) + 500
    #     self.angle = target_angle
    #     # パルス幅を設定してサーボを回転させる
        # self.pi.set_servo_pulsewidth(self.pin, pulse_width)
    #     time.sleep(0.2)  # サーボモータが移動するのを待つために少し待つ

    # def set_ini_angle(self) -> None:
    #     """
    #     サーボモータを初期設定の角度に移動する
    #     """
    #     self.set_angle(self.ini_angle)


    #set_servo_pulsewidthを使わない方法(案)
    def set_angle(self,target_angle: int) ->None:
        if target_angle < self.min_angle or target_angle > self.max_angle:
            print(f"角度は{self.min_angle}から{self.max_angle}度の間で指定してください。")
            return
        #角度[degree]→パルス幅[μs]に変換
        pulse_width = ((target_angle+90) / 180) * (2250 - 750) + 750
        self.angle = target_angle
        #duty比[%]を計算(周期：20ms=20000μs)
        pwm_duty = 100*(pulse_width/20000)
        #duty比をhardware_PWMに使える形に変換(1,000,000を100%と考えて数値を指定するらしい.整数で表したいとかなんとか.)
        duty_cycle = int(pwm_duty* 1000000 / 100)
        frequency = int(self.freq)
        #PWM出力
        self.pi.hardware_PWM(self.pin,frequency,duty_cycle)
    
    def set_ini_angle(self) ->None:
        self.set_angle(self.ini_angle)
    
    

if __name__ == "__main__":
    # 動作サンプル

    """
    動作サンプルではサーボモータを2台接続
    サーボそれぞれの信号ピンを17番、18番に接続
    """
    
    """
    ServoMotorクラスのインスタンス化
    pin: サーボモータ信号端子の接続先ピン番号(設定しない場合 17番)
    max_angle: 最大角度(設定しない場合 180度)
    min_angle: 最小角度(設定しない場合 0度)
    ini_angle: 初期設定角度(設定しない場合 90度)
    """
    
    #これサンプルコードだから0~180のangle採用してる。書き換える必要あり。
    # servo_motor_horizontal = ServoMotor(pin=17, max_angle=160, min_angle=0, ini_angle=90)
    # servo_motor_vertical = ServoMotor(pin=18, max_angle=130, min_angle=0, ini_angle=40)
    sg90 = SG90( pin=17, min_angle=-90, max_angle=90, ini_angle=0,freq=50)

    # サーボ動作開始
    # servo_motor_horizontal.start()
    # servo_motor_vertical.start()
    sg90.start()


    # サンプル動作 
    # servo_motor_vertical.set_angle(20)
    # for angle in range(0, 181, 10):
    #     servo_motor_horizontal.set_angle(angle)

    # servo_motor_vertical.set_angle(40)
    # for angle in range(180, -1, -10):
    #     servo_motor_horizontal.set_angle(angle)

    # servo_motor_vertical.set_angle(60)
    # for angle in range(0, 181, 10):
    #     servo_motor_horizontal.set_angle(angle)
    sg90.set_angle(10)
    print(sg90.angle)

    # 初期位置(ini_angle)に移動
    # servo_motor_vertical.set_ini_angle()
    # servo_motor_horizontal.set_ini_angle()
    sg90.set_ini_angle()
    time.sleep(3)
    # 現在の角度を表示
    # print(servo_motor_vertical.angle)
    # print(servo_motor_horizontal.angle)
    print(sg90.angle)
    time.sleep(3)

    # サーボ動作停止
    # servo_motor_horizontal.stop()
    # servo_motor_vertical.stop()
    sg90.stop()