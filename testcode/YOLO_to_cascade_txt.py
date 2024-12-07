# YOLOデータセットをカスケード分類器用にする計算プログラム

# 入力ファイル名(YOLOファイルを改行で一つのファイルにまとめる(手動))
input_file = 'YOLO_allset.txt'
# 出力ファイル名
output_file = 'poslist_YOLO2cascade.txt'

try:
    # ファイルを読み込んで変換処理
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # YOLOファイルをリスト化
        infile_str = infile.read()
        file_list = infile_str.strip().split("\n")
        print(f"read data: {file_list}")

        for line in file_list:
            # 各データを分割
            # YOLO_allset.txtの形式は"ファイルの名前" "クラス番号" "x1の少数位置" "x2の少数位置" "y1の少数位置" "y2の少数位置" "2つめのクラス番号"～ "画像の横幅" "画像の縦幅"
            parts = line.strip().split()
            if len(parts) >= 8:
                class_num = (len(parts) // 5) - 1
                filename = parts[0]
                outfile.write(f'{filename} {class_num + 1}')

                for num_now in range(class_num + 1):
                    x1 = parts[2 + 5 * num_now]
                    x2 = parts[3 + 5 * num_now]
                    y1 = parts[4 + 5 * num_now]
                    y2 = parts[5 + 5 * num_now]
                    # YOLOテキストファイルの末尾に横の幅，縦の幅を追記する(手動)
                    width = parts[6 + 5 * class_num]
                    height = parts[7 + 5 * class_num]
                    x1, x2, y1, y2 = float(x1), float(x2), float(y1), float(y2)
                    width, height = int(width), int(height)
                    
                    if (x1 > x2):
                        cascado_x1 = int(x2 * width)
                    else:
                        cascado_x1 = int(x1 * width)
                    if (y1 > y2):
                        cascado_y1 = int(y2 * height)
                    else:
                        cascado_y1 = int(y1 * height)

                    cascado_width = int(abs((x2 - x1) * width))
                    cascado_height = int(abs((y2 - y1) * height))

                    if ((cascado_height <= 0) or (cascado_width <= 0)):
                        print(f"warning: width or height less than 0: {line}\nwidth: {cascado_width}(({x2} - {x1}) * {width}), height: {cascado_height}(({y2} - {y1}) * {height})")

                    # print(f"cascade: {cascado_x1} {cascado_y1} {cascado_width} {cascado_height}")
                    
                    # 対象カラーコーンの場所を記述
                    new_line = f" {cascado_x1} {cascado_y1} {cascado_width} {cascado_height}"
                    outfile.write(new_line)

                outfile.write('\n')
            else:
                print(f"data parts is not correct. data parts is 5: {len(parts)} at {line}")

        print(f"converting finished. result saved {output_file}.")

except Exception as e:
    print(f"failed convert: {e}")

        



        

        
        
    
