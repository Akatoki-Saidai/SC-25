from bmp280 import BMP280
from bno055 import BNO055
# from sg90 import SG90
from log import logger
from micropyGPS import MicropyGPS
from motor import Motor

def setup():
    try:
        # BMPをセットアップ
        bmp = BMP280()

        # BNOをセットアップ
        bno = BNO055()
        if not bno.begin():
            logger.critical('Failed to initialize BNO055! Is the sensor connected?')
        
        # カメラをセットアップ
        # 保留

        # GNSS (BE-180) をセットアップ
        gnss = MicropyGPS(9, 'dd')
        # ↑メモ　もう少しいじりたい

        # モーターをセットアップ
        motor = Motor(right_pin1=20, right_pin2=21, left_pin1=5, left_pin2=7)

        # サーボモーターのセットアップ
        # servo = SG90(pin=26, min_angle=-90, max_angle=90, ini_angle=0, freq=50)

        # スピーカーのセットアップ
        # 保留


    except Exception as e:
        logger.exception("An error occured in setup")
