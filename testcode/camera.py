# camera lib

import time
from ultralytics import YOLO
import cv2
import numpy as np


# 同じディレクトリに重みを置く
pt_path = "./SC-25_yolomodel_v2.pt"

class Camera:
    def yolo_detect(self, frame):
        
        # YOLOv10nモデルをロード
        model = YOLO(pt_path)
        # 推論
        yolo_results = model(frame, save = True, show = True)

        confidence_best = 0
        # 最も信頼性の高いBounding Boxを取得
        Bounding_box = yolo_results.pandas().xyxy[0]
        # print(Bounding_box)
        for i in range(len(Bounding_box)):
            confidence = Bounding_box.confidence[i]
            # name = Bounding_box.name[i]
            if confidence < confidence_best:
                continue
            else:
                confidence_best = confidence
            xmin = Bounding_box.xmin[i]
            ymin = Bounding_box.ymin[i]
            xmax = Bounding_box.xmax[i]
            ymax = Bounding_box.ymax[i]
        
        center_x = (xmax - xmin) / 2
        yolo_xylist = [xmin, ymin, xmax, ymax, confidence]

        return yolo_xylist, center_x


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

            # cv2.putText(frame, str(center_x), (center_x, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1)

            return area, center_x, center_y


    def judge_cone(self, frame, yolo_xylist, yolo_center_x, red_area):
            frame_center_x = frame.shape[1] // 2

            # 中心座標のx座標が画像の中心より大きいか小さいか判定
            if red_area > 7000:
                print("Close enough to red")
                camera_order = 4

            elif red_area > 10:
                if frame_center_x -  50 <= yolo_center_x <= frame_center_x + 50:
                    print("The red object is in the center")#直進
                    camera_order = 1
                elif yolo_center_x > frame_center_x + 50:
                    print("The red object is in the right")#右へ
                    camera_order = 2
                elif yolo_center_x < frame_center_x - 50:
                    print("The red object is in the left")#左へ
                    camera_order = 3

                else:
                    print("The red object is too minimum")
            
            else:
                print("The red object is None")
            
            # Bounding Box描画
            cv2.rectangle(frame, (yolo_xylist[0], yolo_xylist[1]), (yolo_xylist[2], yolo_xylist[3]), (0, 0, 255), 2)
            cv2.putText(frame, str(yolo_xylist[4]), (yolo_xylist[0], yolo_xylist[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255))

            # 面積表示
            cv2.putText(frame, str(red_area), (10, 40, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255)))

            # red_result = cv2.drawContours(mask, [biggest_contour], -1, (0, 255, 0), 2)
            

            return frame, camera_order

if __name__ == '__main__':
    
    from picamera2 import Picamera2 

    # カメラセットアップ
    try:
        CameraStart = False
        picam2 = Picamera2()
        config = picam2.create_preview_configuration({"format": 'XRGB8888', "size": (320, 240)})
        picam2.configure(config)
        cam = Camera()

        picam2.start()

        while True:
            frame = picam2.capture_array()

            # YOLO
            yolo_xylist, yolo_center_x = cam.yolo_detect(frame)
            # 赤色検出
            mask = cam.red_detect(frame)
            red_area, _red_x, _red_y = cam.analyze_red(frame, mask)
            print("red area: ", red_area)
            
            # 判断
            frame, camera_order = cam.judge_cone(frame, yolo_xylist, yolo_center_x, red_area)
            

            # 結果表示
            cv2.imshow('kekka', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print('q interrupted direction by camera')
                continue

            time.sleep(1)


    except Exception as e:
        print(f"An error occurred in init camera: {e}")
        
