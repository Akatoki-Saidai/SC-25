import threading
import time

from bmp280 import BMP280
from bno055 import BNO055
from camera import Camera
from gnss import GNSS
# from sg90 import SG90
import sc_logging
from motor import Motor

logger = sc_logging.get_logger(__name__)

# 各デバイスのセットアップ devices引数の中身を変更します
def setup(devices):
    try:
        # BMPをセットアップ
        devices["bmp"] = BMP280()

        # BNOをセットアップ
        devices["bno"] = BNO055()
        if not devices["bno"].begin():
            logger.critical('Failed to initialize BNO055! Is the sensor connected?')
        
        # カメラをセットアップ
        devices["camera"] = Camera()

        # GNSS (BE-180) をセットアップ
        devices["gnss"] = GNSS()

        # モーターをセットアップ
        devices["motor"] = Motor(right_pin1=20, right_pin2=21, left_pin1=5, left_pin2=7)

        # サーボモーターのセットアップ
        # devices["servo"] = SG90(pin=26, min_angle=-90, max_angle=90, ini_angle=0, freq=50)

        # スピーカーのセットアップ
        # 保留


    except Exception as e:
        logger.exception("An error occured in setup")


# 待機フェーズ
def wait_phase(devices, data):
    logger.info("Entered wait phase")
    data["phase"] = "wait"
    # 高度が高くなるまで待つ
    while True:
        time.sleep(0.1)
        # 高度が十分高かったら，待機フェーズを終了
        if 20 < data["alt"]:
            break

# 落下フェーズ
def fall_phase(devices, data):
    logger.info("Entered fall phase")
    data["phase"] = "fall"

# 遠距離フェーズ
def long_phase(devices, data):
    logger.info("Entered long phase")
    data["phase"] = "long"

# 近距離フェーズ
def short_phase(devices, data):
    logger.info("Entered short phase")
    data["phase"] = "short"

# ゴールフェーズ
def goal_phase(devices, data):
    logger.info("Entered goal phase")
    data["phase"] = "goal"

def main():
    # 使用するデバイス  変数の中身をこの後変更する
    devices = {
        "bmp": None,
        "bno": None,
        "camera": None,
        "gnss": None,
        "motor": None,
        "servo": None,
        "speaker": None
    }

    # 各デバイスのセットアップ  devicesの中に各デバイスの変数を入れる
    setup(devices)

    # 取得したデータ  新たなデータを取得し次第，中身を更新する
    data = {"phase": None, "lat": None, "lon": None, "alt": None, "temp": None, "press": None, "camera_order": None, "accel": [None, None, None], "line_accel": [None, None, None], "mag": [None, None, None], "gyro": [None, None, None], "grav": [None, None, None]}

    # 並行処理でBMP280による測定をし続け，dataに代入し続ける
    get_bmp_thread = threading.Thread(target=devices["bmp"].get_forever, args=(data,))
    get_bmp_thread.start()  # BMP280による測定をスタート
    
    # 並行処理でBNO055による測定をし続け，dataに代入し続ける
    get_bno_thread = threading.Thread(target=devices["bno"].get_forever, args=(data,))
    get_bno_thread.start()  # BNO055による測定をスタート

    # 並行処理でGNSSによる測定をし続け，dataに代入し続ける
    get_gnss_thread = threading.Thread(target=devices["gnss"].get_forever, args=(data,))
    get_gnss_thread.start()  # GNSSによる測定をスタート

    # 待機フェーズを実行
    wait_phase(devices, data)

    # 落下フェーズを実行
    fall_phase(devices, data)

    # 遠距離フェーズを実行
    long_phase(devices, data)

    # 短距離フェーズを実行
    short_phase(devices, data)

    # ゴールフェーズを実行
    goal_phase(devices, data)

if __name__ == "__main__":
    main()