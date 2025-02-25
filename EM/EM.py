from threading import Thread
from multiprocessing import Process, Value
import time

from bmp280 import BMP280
from bno055 import BNO055
from camera import Camera
from gnss import GNSS
# from sg90 import SG90
import sc_logging
from motor import Motor
import speaker
import start_gui

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

        # GNSS (BE-180) をセットアップ
        devices["gnss"] = GNSS()

        # モーターをセットアップ
        devices["motor"] = Motor(right_pin1=20, right_pin2=21, left_pin1=5, left_pin2=7)

        # サーボモーターのセットアップ
        # devices["servo"] = SG90(pin=26, min_angle=-90, max_angle=90, ini_angle=0, freq=50)

        # スピーカーのセットアップ
        # 不要
    except Exception as e:
        logger.exception("An error occured in setup")

# カメラの処理が重いので，カメラだけ完全に分離してセットアップ+撮影
def camera_setup_and_start(camera_order, show=False):
    camera = Camera()  # セットアップ
    camera.start()  # 起動
    # カメラで画像認識し続ける
    camera_thread = Thread(target=camera.get_forever, args=(camera_order, show,))
    camera_thread.start()

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
def short_phase(devices, data, camera_order):
    logger.info("Entered short phase")
    data["phase"] = "short"
    while True:
        logger.info(f"camera_order: {camera_order.value}")
        time.sleep(1)

# ゴールフェーズ
def goal_phase(devices, data):
    logger.info("Entered goal phase")
    data["phase"] = "goal"

if __name__ == "__main__":
    # 使用するデバイス  変数の中身をこの後変更する
    devices = {
        "bmp": None,
        "bno": None,
        "gnss": None,
        "motor": None,
        "servo": None
    }

    # 各デバイスのセットアップ  devicesの中に各デバイスの変数を入れる
    setup(devices)

    # 取得したデータ  新たなデータを取得し次第，中身を更新する
    data = {"phase": None, "lat": None, "lon": None, "alt": None, "temp": None, "press": None, "accel": [None, None, None], "line_accel": [None, None, None], "mag": [None, None, None], "gyro": [None, None, None], "grav": [None, None, None]}

    # 並行処理でBMP280による測定をし続け，dataに代入し続ける
    bmp_thread = Thread(target=devices["bmp"].get_forever, args=(data,))
    bmp_thread.start()  # BMP280による測定をスタート
    
    # 並行処理でBNO055による測定をし続け，dataに代入し続ける
    bno_thread = Thread(target=devices["bno"].get_forever, args=(data,))
    bno_thread.start()  # BNO055による測定をスタート

    # 並行処理でGNSSによる測定をし続け，dataに代入し続ける
    gnss_thread = Thread(target=devices["gnss"].get_forever, args=(data,))
    gnss_thread.start()  # GNSSによる測定をスタート

    # 待機フェーズを実行
    wait_phase(devices, data)

    # 落下フェーズを実行
    fall_phase(devices, data)

    # 遠距離フェーズを実行
    long_phase(devices, data)

    # 並列処理でカメラをセットアップして撮影開始（並行処理ではない）
    # カラーコーンの位置を camera_order.value に代入し続ける
    camera_order = Value('i', 0)  # 別のプロセスとデータをやり取りするのでcamera_orderだけ特殊な扱い
    camera_process = Process(target=camera_setup_and_start, args=(camera_order, True))
    camera_process.start()  # 画像認識スタート

    # 短距離フェーズを実行
    short_phase(devices, data, camera_order)

    # ゴールフェーズを実行
    goal_phase(devices, data)