import copy
from threading import Thread
from multiprocessing import Process, Value
import time

import pigpio

from bmp280 import BMP280
from bno055 import BNO055
from camera import Camera
from gnss import GNSS
from sg90 import SG90
import sc_logging
from motor import Motor
import speaker
import start_gui

logger = sc_logging.get_logger(__name__)

NICR_PIN = 10  # ニクロム線のGPIO番号

GOAL_LAT = 35.862831  # ゴールの緯度
GOAL_LON = 139.608850  # ゴールの経度

# 各デバイスのセットアップ devices引数の中身を変更します
def setup(devices):
    try:
        # BMPをセットアップ
        devices["bmp"] = BMP280(logger=logger)

        # BNOをセットアップ
        devices["bno"] = BNO055(logger=logger)
        if not devices["bno"].begin():
            logger.critical('Failed to initialize BNO055! Is the sensor connected?')

        # GNSS (BE-180) をセットアップ
        devices["gnss"] = GNSS(logger=logger)

        # モーターをセットアップ
        devices["motor"] = Motor(right_pin1=20, right_pin2=21, left_pin1=5, left_pin2=7, logger=logger)

        # サーボモーターのセットアップ
        devices["servo"] = SG90(pin=26, min_angle=-90, max_angle=90, ini_angle=0, freq=50, logger=logger)

        # pigpioのセットアップ(omusubi0はpigpio自動有効化設定済)
        devices["pi"] = pigpio.pi()
        # NiCr線のセットアップ
        devices["pi"].set_mode(NICR_PIN, pigpio.OUTPUT)  # NiCrのピンを出力モードに設定
        devices["pi"].write(NICR_PIN, 0)  # NiCrをオフにしておく

        # スピーカーのセットアップ
        devices["speaker"] = Speaker()
        # LEDのセットアップ
        ## 基板にLEDをつけ忘れた...
    except Exception as e:
        logger.exception(f"An error occured in setup device: {e}")

# カメラの処理が重いので，カメラだけ完全に分離してセットアップ+撮影
def camera_setup_and_start(camera_order, show=False):
    try:
        camera = Camera(logger, show=show, save=True)  # セットアップ
        camera.start()  # 起動
        # カメラで画像認識し続ける
        camera_thread = Thread(target=camera.get_forever, args=(camera_order, show,))
        camera_thread.start()
    except Exception as e:
        logger.exception(f"An error occured in setup and start camera: {e}")

# 待機フェーズ
def wait_phase(devices, data):
    try:
        logger.info("Entered wait phase")
        data["phase"] = "wait"
    except Exception as e:
        logger.exception(f"An error occured in Entering wait phase:{e}")
    
    # 高度が高くなるまで待つ
    while True:
        try:
            time.sleep(0.1)
            # 高度が十分高かったら
            if 20 < data["alt"]:
                old_alt = data["alt"]
                time.sleep(3)
                # 少し待ってもまだ高度が高く，かつ高度が少しでも変化していたら，待機フェーズを終了
                if 20 < data["alt"] and old_alt != data["alt"]:
                    break
        except Exception as e:
            logger.exception(f"An error occured in wait phase:{e}")

# 落下フェーズ
def fall_phase(devices, data):
    try:
        logger.info("Entered fall phase")
        data["phase"] = "fall"
    except Exception as e:
        logger.exception(f"An error occured in Entering wait phase: {e}")
                         
    # 落下して静止するまで待つ
    while True:
        try:
            time.sleep(0.1)
            # 地面近くで静止してたら
            if data["alt"] < 5 and sum(abs(accel_xyz) for accel_xyz in data["accel"]) < 0.5 and sum(abs(gyro_xyz) for gyro_xyz in data["gyro"]) < 0.05:
                old_accel, old_gyro = copy.copy(data["accel"]), copy.copy(data["gyro"])
                time.sleep(3)
                # 少し待ってもまだ静止して，かつ値が変化していたら
                if sum(abs(accel_xyz) for accel_xyz in data["accel"]) < 0.5 and sum(abs(gyro_xyz) for gyro_xyz in data["gyro"]) < 0.05 and old_accel != data["accel"] and old_gyro != data["gyro"]:
                    # NiCr線を焼き切る
                    logger.info("nicr turned on")  # ここで音を鳴らしてもいいかも
                    devices["pi"].write(NICR_PIN, 1)  # NiCr ON
                    time.sleep(10)
                    devices["pi"].write(NICR_PIN, 0)  # NiCr OFF
                    logger.info("nicr turned off")
                    break
        except Exception as e:
            logger.exception(f"An error occured in fall phase: {e}")

# 遠距離フェーズ
def long_phase(devices, data):
    try:
        logger.info("Entered long phase")
        data["phase"] = "long"
    except Exception as e:
        logger.exception(f"An error occured in Entering long phase: {e}")

    # 機体がひっくり返っていたら回る
    try:
        if data["gyro"][2] < 0:  #################要変更#####################本当に負なのか，z軸は2なのか
            start_time = time.time()
            devices["motor"].accel()
            logger.info("muki_hantai")
            while data["gyro"][2] < 0 and time.time()-start_time < 5:  #################要変更#####################本当に負なのか，z軸は2なのか
                pass
            devices["motor"].stop()
    except Exception as e:
        logger.exception(f"An error occured in muki_hantai: {e}")
    
    # ゴールから離れている間，ゴールに向かって進む
    while True:
        try:
            time.sleep(0.1)
            if data["goal_angle"] < 30 or 330 <= data["goal_angle"]:
                devices["motor"].accel()  # 前進
            elif 30 <= data["goal_angle"] < 180:
                devices["motor"].rightturn()  # 右へ
            elif 180 <= data["goal_angle"] < 330:
                devices["motor"].leftturn()  # 左へ
            
            # ゴールに近づいたら近距離フェーズへ
            if data["goal_distance"] < 5:
                break
        except Exception as e:
            logger.exception(f"An error occured in long phase approaching: {e}")

# 近距離フェーズ
def short_phase(devices, data, camera_order):
    try:
        logger.info("Entered short phase")
        data["phase"] = "short"
    except Exception as e:
        logger.exception(f"An error occured in entering short phase: {e}")

    while True:
        try:
            time.sleep(0.1)
            if camera_order.value == 0:
                # コーンが見つからなかったとき
                devices["motor"].rightturn()
                time.sleep(0.5)
                devices["motor"].stop()
            elif camera_order.value == 1:
                # コーンが正面にあったとき
                devices["motor"].accel()
            elif camera_order.value == 2:
                # コーンが右にあったとき
                devices["motor"].rightturn()
            elif camera_order.value == 3:
                # コーンが左にあったとき
                devices["motor"].leftturn()
            elif camera_order.value == 4:
                # コーンが十分に大きく見えるとき，ゴールフェーズへ
                break
        except Exception as e:
            logger.exception(f"An error occured in short phase moving: {e}")


# ゴールフェーズ
def goal_phase(devices, data):
    try:
        logger.info("Entered goal phase")
        data["phase"] = "goal"
        while True:
            time.sleep(1)
    except Exception as e:
        logger.exception(f"An error occured in goal phase: {e}")


if __name__ == "__main__":
    # 使用するデバイス  変数の中身をこの後変更する
    devices = {
        "bmp": None,
        "bno": None,
        "gnss": None,
        "motor": None,
        "servo": None,
        "pi": None,
        "speaker":None
    }

    # 各デバイスのセットアップ  devicesの中に各デバイスのインスタンスを入れる
    setup(devices)

    # 取得したデータ  新たなデータを取得し次第，中身を更新する
    data = {"phase": None, "lat": None, "lon": None, "datetime_gnss": None, "alt": None, "temp": None, "press": None, "accel": [None, None, None], "line_accel": [None, None, None], "mag": [None, None, None], "gyro": [None, None, None], "grav": [None, None, None], "goal_distance": None, "goal_angle": None, "goal_lat": GOAL_LAT, "goal_lon": GOAL_LON}

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
    # 画像認識の結果を camera_order.value に代入し続ける
    camera_order = Value('i', 0)  # 別のプロセスとデータをやり取りするのでcamera_orderだけ特殊な扱い
    camera_process = Process(target=camera_setup_and_start, args=(camera_order, True))
    camera_process.start()  # 画像認識スタート

    # 短距離フェーズを実行
    short_phase(devices, data, camera_order)

    # ゴールフェーズを実行
    goal_phase(devices, data)