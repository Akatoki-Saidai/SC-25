from ultralytics import YOLO

# YOLOv10nモデルをロード
model = YOLO("yolov10n.pt")

# モデルをyamlファイルでトレーニング
model.train(data="C:/Users/hiyos/OneDrive - 埼玉大学/あかとき/プログラム/SC-25/yolo_class1/dataset/training.yaml", epochs=100, imgsz=640)

# モデルをエクスポート
# model.save("yolov10n_test.pt")
