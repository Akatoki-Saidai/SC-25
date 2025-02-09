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
            # YOLO_allset.txtの形式は"ファイルの名前" "クラス番号" "xの中心位置" "yの中心位置" "xの幅" "yの幅" "2つめのクラス番号"～ "画像の横幅" "画像の縦幅"
            parts = line.strip().split()
            if len(parts) >= 8:
                class_num = (len(parts) // 5) - 1
                filename = parts[0]
                outfile.write(f'{filename} {class_num + 1}')

                for num_now in range(class_num + 1):
                    x_center = parts[2 + 5 * num_now]
                    y_center = parts[3 + 5 * num_now]
                    x_width = parts[4 + 5 * num_now]
                    y_height = parts[5 + 5 * num_now]
                    # YOLOテキストファイルの末尾に横の幅，縦の幅を追記する(手動)
                    width = parts[6 + 5 * class_num]
                    height = parts[7 + 5 * class_num]
                    x_center, y_center, x_width, y_height = float(x_center), float(y_center), float(x_width), float(y_height)
                    width, height = int(width), int(height)


                    cascado_width = abs(x_width * width)
                    cascado_height = abs(y_height * height)

                    cascado_x1 = int((x_center * width) - (cascado_width / 2))
                    cascado_y1 = int((y_center * height) - (cascado_height / 2))

                    if ((cascado_x1 <= 0) or (cascado_y1 <= 0)):
                        print(f"warning: x1 or y1 less than 0: {line}\nx1: {cascado_x1}({x_center} - ({cascado_width} / 2)), y1: {cascado_y1}({y_center} - ({cascado_height} / 2))")

                    cascado_width = int(cascado_width)
                    cascado_height = int(cascado_height)

                    if ((cascado_height <= 0) or (cascado_width <= 0)):
                        print(f"warning: width or height less than 0: {line}\nwidth: {cascado_width}(({x_width} * {width}), height: {cascado_height}(({y_height} * {height})")

                    # print(f"cascade: {cascado_x1} {cascado_y1} {cascado_width} {cascado_height}")
                    
                    # 対象カラーコーンの場所を記述
                    new_line = f" {cascado_x1} {cascado_y1} {cascado_width} {cascado_height}"
                    outfile.write(new_line)
                
                # 最後の要素では改行しない
                if line < len(file_list) - 1:
                    outfile.write('\n')
            else:
                print(f"data parts is not correct. data parts is 5: {len(parts)} at {line}")


        print(f"converting finished. result saved {output_file}.")

except Exception as e:
    print(f"failed convert: {e}")

        



        

        
        
    
