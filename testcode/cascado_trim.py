import cv2
import os

text_file_path = "pos/poslist.txt"
output_dir = "pos_trim"

try:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(text_file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        # 読み込み
        parts = line.strip().split()
        image_path = os.path.join("pos", parts[0])
        object_count = int(parts[1])
        regions = parts[2:]

        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            continue

        # 各領域を切り抜く
        for i in range(object_count):
            x, y, w, h = map(int, regions[i * 4:(i + 1) * 4])
            cropped = image[y:y + h, x:x + w]  
            if cropped.size == 0:
                print(f"Invalid region in {image_path}: x={x}, y={y}, w={w}, h={h}")
                continue

            # 保存
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(output_dir, f"{name}_crop_{i+1}{ext}")

            cv2.imwrite(output_path, cropped)

except Exception as e:
    print(f"failed to trim: {e}")


print("Cropping completed.")
