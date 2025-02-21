from threading import Thread
import time

from bmp280 import BMP280
from bno055 import BNO055
from camera import Camera
# from sg90 import SG90
import sc_logging
from micropyGPS import MicropyGPS
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
        devices["gnss"] = MicropyGPS(9, 'dd')
        # ↑メモ　もう少しいじりたい

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
    logger.info("Entered waiting phase")
    data["phase"] = "wait"
    # 高度を並行処理で測定し続け，dataに代入し続ける
    get_alt_thread = Thread(target=devices["bmp"].get_altitude_forever, args=(data,), daemon=True)
    get_alt_thread.start()  # 高度の測定スタート
    # 高度が高くなるまで待つ
    while True:
        time.sleep(0.1)
        # 高度が十分高かったら，待機フェーズを終了
        if 20 < data["alt"]:
            break

# 落下フェーズ
def fall_phase(devices, data):
    pass

# 遠距離フェーズ
def long_phase(devices, data):
    pass

# 近距離フェーズ
def short_phase(devices, data):
    pass

# ゴールフェーズ
def goal_phase(devices, data):
    pass

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

    # 各デバイスのセットアップ  devicesの中に各デバイスのインスタンスを入れる
    setup(devices)

    # 取得したデータ  新たなデータを取得し次第，中身を更新する
    data = {"phase": None, "lat": None, "lon": None, "alt": None, "temp": None, "press": None, "camera_order": None, "accel": [None, None, None], "mag": [None, None, None], "gyro": [None, None, None]}

    # 並列処理で待機フェーズを実行
    wait_thread = Thread(target=wait_phase, args=(devices, data,))
    wait_thread.start()  # 待機フェーズを開始する
    wait_thread.join()  # 待機フェーズが終わるまで待機

    # 並列処理で落下フェーズを実行
    fall_thread = Thread(target=fall_phase, args=(devices, data,))
    fall_thread.start()  # 落下フェーズを開始する
    fall_thread.join()  # 落下フェーズが終わるまで待機

    # 並列処理で遠距離フェーズを実行
    long_thread = Thread(target=long_phase, args=(devices, data,))
    long_thread.start()  # 遠距離フェーズを開始する
    long_thread.join()  # 遠距離フェーズが終わるまで待機

    # 並列処理で短距離フェーズを実行
    short_thread = Thread(target=short_phase, args=(devices, data,))
    short_thread.start()  # 短距離フェーズを開始する
    short_thread.join()  # 短距離フェーズが終わるまで待機

    # 並列処理でゴールフェーズを実行
    goal_thread = Thread(target=goal_phase, args=(devices, data,))
    goal_thread.start()  # ゴールフェーズを開始する
    goal_thread.join()  # ゴールフェーズが終わるまで待機

if __name__ == "__main__":
    main()