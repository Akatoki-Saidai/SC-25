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
    def __init__(self, pin=18, min_angle=-90, max_angle=90, ini_angle=0,freq=50):
        self.pin = pin
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.angle = 0
        self.ini_angle = ini_angle
        self.pi = None
        self.freq = freq

    def start(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

    def stop(self):
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.stop()

    #set_servo_pulsewidthを使わない方法(案)
    def set_angle(self,target_angle):
        if target_angle < self.min_angle or target_angle > self.max_angle:
            print(f"角度は{self.min_angle}から{self.max_angle}度の間で指定してください。")
            return
        #角度[degree]→パルス幅[μs]に変換
        pulse_width = ((target_angle+90.0)/180.0)*1900.0+500.0
        self.angle = target_angle
        #duty比[%]を計算(周期：20ms=20000μs)
        pwm_duty = 100.0*(pulse_width/20000.0)
        #duty比をhardware_PWMに使える形に変換(1,000,000を100%と考えて数値を指定するらしい.整数で表したいとかなんとか.)
        duty_cycle = int(pwm_duty* 1000000 / 100)
        frequency = int(self.freq)
        #PWM出力
        self.pi.hardware_PWM(self.pin,frequency,duty_cycle)
    
    def set_ini_angle(self):
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
    sg90 = SG90( pin=18, min_angle=-70, max_angle=70, ini_angle=0,freq=50)

    # サーボ動作開始
    sg90.start()

    # サンプル動作 
    print(sg90.angle)

    # 初期位置(ini_angle)に移動
    sg90.set_ini_angle()
    time.sleep(3)
    # 現在の角度を表示
    print(sg90.angle)
    time.sleep(3)

    # サーボ動作停止
    sg90.stop()