from ultralytics import YOLO

# YOLOv10nモデルをロード
model = YOLO("yolov10n.pt")

# モデルをyamlファイルでトレーニング
model.train(data="./datasets/dataset/training.yaml", epochs=100, imgsz=640)

# モデルをエクスポート
# model.save("yolov10n_test.pt")
