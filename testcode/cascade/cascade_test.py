import cv2
from picamera2 import Picamera2

try:
	# カメラの設定
	picam2 = Picamera2()
	config = picam2.create_preview_configuration({"format": 'XRGB8888', "size": (416, 416)})
	#config["main"]
	picam2.configure(config)

except Exception as e:
	print(f"An error occured in setting camera: {e}")


try:
	# カスケード分類器読み込み(パス要確認)
	cascade_file = "./vec/vec_fin/SC_null_110.xml"
	# cascade_file = "SC_null_1000x_straight.xml"
	cascade = cv2.CascadeClassifier(cascade_file)

except Exception as e:
	print(f"An error occured in reading cascade file: {e}")
 
# カメラ起動
try:
	picam2.start()

except Exception as e:
	print(f"An error occured in booting camera: {e}")


while True:

	try:
		frame = picam2.capture_array()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


		colorcoon = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(10, 10))
			
		# 顔領域を赤色の矩形で囲む
		for (x, y, w, h) in colorcoon:
			cv2.rectangle(frame, (x, y), (x + w, y+h), (0,0,200), 3)

		#結果画像を表示
		cv2.imshow('cascade', frame)
		if cv2.waitKey(25) & 0xFF == ord('q'):
			break

	
	except Exception as e:
		print(f"An error occured in cascade classifier: {e}")


