# camera lib
import time
import cv2
import numpy as np
from picamera2 import Picamera2
import pigpio


class SG90:
    """SG90を制御するクラス

    pin: GPIOのピン番号
    max_angle: 最大移動角度
    min_angle: 最小移動角度
    angle: 現在の角度
    ini_angle: 初期設定角度
    pi: gpio制御
    """
    def __init__(self, pin, min_angle=0, max_angle=180, ini_angle=0, freq=50):
        """サーボモータをセットアップ"""
        self._pin = pin
        self._max_angle = max_angle
        self._min_angle = min_angle
        self._angle = 0
        self._ini_angle = ini_angle
        self._freq = freq
        self._range = 255

        self._pi = pigpio.pi()
        self._pi.set_mode(self._pin, pigpio.OUTPUT)

        self.set_ini_angle()
    
    def __del__(self):
        """サーボモータを終了"""
        if self._pi.connected:
            self._pi.set_mode(self._pin, pigpio.INPUT)
            # self._pi.stop()

    def get_angle(self):
        """サーボモータの角度を取得"""
        return self._angle

    #set_servo_pulsewidthを使わない方法(案)
    def set_angle(self, target_angle):
        """サーボモータの角度を特定の角度に動かす"""
        if target_angle < self._min_angle or target_angle > self._max_angle:
            print(f"角度は{self._min_angle}から{self._max_angle}度の間で指定してください。")
            return
        
        #角度[degree]→パルス幅[μs]に変換
        pulse_width = ((target_angle)/180.0) * 1900.0+500.0
        self._angle = target_angle
        #duty比[%]を計算(周期：20ms=20000μs)
        pwm_duty = 100.0 * (pulse_width/20000.0)
        #duty比をhardware_PWMに使える形に変換(1,000,000を100%と考えて数値を指定するらしい.整数で表したいとかなんとか.)
        duty_cycle = int(pwm_duty * 1000000 / 100)
        frequency = int(self._freq)
        
        #PWM出力
        # hardware-PWM バージョン
        # self.pi.hardware_PWM(self.pin,frequency,duty_cycle)
        # software-PWM バージョン
        self._pi.set_PWM_frequency(self._pin, frequency)
        self._pi.set_PWM_range(self._pin, self._range)
        self._pi.set_PWM_dutycycle(self._pin, int((pwm_duty / 100) * self._range))

        print(f"servo_angle: {self._angle}")
    
    def set_ini_angle(self):
        self.angle = self._ini_angle


class Camera:
    def red_detect(self, frame):
        # HSV色空間に変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 赤色のHSVの値域1
        hsv_min = np.array([0, 117, 104])
        hsv_max = np.array([11, 255, 255])
        mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

        # 赤色のHSVの値域2
        hsv_min = np.array([169, 117, 104])
        hsv_max = np.array([179, 255, 255])
        mask2 = cv2.inRange(hsv, hsv_min, hsv_max)

        return mask1 + mask2


    def analyze_red(self, frame, mask):
            
        camera_order = 0
        # 画像の中にある領域を検出する
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
        #画像の中に赤の領域があるときにループ
        if 0 < len(contours):
                        
            # 輪郭群の中の最大の輪郭を取得する-
            biggest_contour = max(contours, key=cv2.contourArea)

            # 最大の領域の外接矩形を取得する
            rect = cv2.boundingRect(biggest_contour)

            # #最大の領域の中心座標を取得する
            center_x = (rect[0] + rect[2] // 2)
            center_y = (rect[1] + rect[3] // 2)

            # 最大の領域の面積を取得する-
            area = cv2.contourArea(biggest_contour)

            # 最大の領域の長方形を表示する
            cv2.rectangle(frame, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 0, 255), 2)

            # 最大の領域の中心座標を表示する
            cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
            cv2.putText(frame, str(center_x), (rect[0], rect[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 1)

            # 最大の領域の面積を表示する
            # cv2.putText(frame, str(area), (rect[0], rect[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)

            # cv2.putText(frame, str(center_x), (center_x, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1)


            frame_center_x = frame.shape[1] // 2

            # 中心座標のx座標が画像の中心より大きいか小さいか判定
            if area > 7000:
                print("Close enough to red")
                camera_order = 4

            elif area > 10:
                if frame_center_x -  50 <= center_x <= frame_center_x + 50:
                    print("The red object is in the center")#直進
                    camera_order = 1
                elif center_x > frame_center_x + 50:
                    print("The red object is in the right")#右へ
                    camera_order = 2
                elif center_x < frame_center_x - 50:
                    print("The red object is in the left")#左へ
                    camera_order = 3

            else:
                print("The red object is too minimum")

            # red_result = cv2.drawContours(mask, [biggest_contour], -1, (0, 255, 0), 2)
        
        else:
            print("The red object is None")
            
        # cv2.imshow("Frame", frame)
        # cv2.imshow("Mask", mask)

        return frame, camera_order

if __name__ == '__main__':
    sg90 = SG90(pin=26, min_angle=-90, max_angle=90, ini_angle=0, freq=50)

    picam2 = Picamera2()
    config = picam2.create_preview_configuration({"format": 'XRGB8888', "size": (320, 240)})
    picam2.configure(config)
    cam = Camera()
    picam2.start()

    while True:
        frame = picam2.capture_array()
        mask = cam.red_detect(frame)
        # 赤色検知の結果を取得
        # analize_redの戻り値は0が見つからない，1が中心，2が右，3が左，4がゴール
        frame, camera_order = cam.analyze_red(frame, mask)
        # 結果表示
        cv2.imshow('kekka', frame)
        time.sleep(3)
        #print(len(contours))

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            print('q interrupted direction by camera')
            continue
            
        sg90.set_angle(-15)
        frame = picam2.capture_array()
        mask = cam.red_detect(frame)
        # 赤色検知の結果を取得
        # analize_redの戻り値は0が見つからない，1が中心，2が右，3が左，4がゴール
        frame, camera_order = cam.analyze_red(frame, mask)
        # 結果表示
        cv2.imshow('kekka', frame)
        time.sleep(3)
        #print(len(contours))

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            print('q interrupted direction by camera')
            continue


        sg90.set_angle(15)
        frame = picam2.capture_array()
        cam.red_detect(frame)
        mask = cam.red_detect(frame)
        # 赤色検知の結果を取得
        # analize_redの戻り値は0が見つからない，1が中心，2が右，3が左，4がゴール
        frame, camera_order = cam.analyze_red(frame, mask)
        # 結果表示
        cv2.imshow('kekka', frame)
        time.sleep(3)
        #print(len(contours))

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            print('q interrupted direction by camera')
            continue

