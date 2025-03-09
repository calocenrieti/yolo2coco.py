import os
import json
from PIL import Image

def yolo_to_coco(yolo_ann_dir, img_dir, output_file):
    # COCOフォーマットの基本構造
    coco = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    category_set = set()
    category_mapping = {}
    annotation_id = 1
    image_id = 1

    # カテゴリの登録（必要に応じてクラス名を指定）
    for txt_file in os.listdir(yolo_ann_dir):
        if not txt_file.endswith('.txt'):
            continue
        img_name = txt_file.replace('.txt', '.png')  # 画像拡張子は適宜変更
        img_path = os.path.join(img_dir, img_name)
        if not os.path.exists(img_path):
            print(f"画像が見つかりません: {img_path}")
            continue

        # 画像情報の取得
        with Image.open(img_path) as img:
            width, height = img.size

        image_info = {
            "id": image_id,
            "file_name": img_name,
            "width": width,
            "height": height
        }
        coco["images"].append(image_info)

        # アノテーションの読み込み
        txt_path = os.path.join(yolo_ann_dir, txt_file)
        with open(txt_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                bbox_width = float(parts[3])
                bbox_height = float(parts[4])

                # 相対座標を絶対座標に変換
                x_min = (x_center - bbox_width / 2) * width
                y_min = (y_center - bbox_height / 2) * height
                abs_width = bbox_width * width
                abs_height = bbox_height * height

                # カテゴリの登録
                if class_id not in category_mapping:
                    category_mapping[class_id] = len(category_mapping) + 1
                    category_info = {
                        "id": category_mapping[class_id],
                        "name": str(class_id)  # クラス名がある場合は変更
                    }
                    coco["categories"].append(category_info)

                annotation = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": category_mapping[class_id],
                    "bbox": [x_min, y_min, abs_width, abs_height],
                    "area": abs_width * abs_height,
                    "iscrowd": 0
                }
                coco["annotations"].append(annotation)
                annotation_id += 1

        image_id += 1

    # JSONファイルに書き込み
    with open(output_file, 'w') as f:
        json.dump(coco, f, ensure_ascii=False, indent=4)

# 使用方法
yolo_annotation_dir = "path\to\yolo_annotation_dir"
image_directory = "path\to\image_directory"               # 画像ファイルのディレクトリパス
output_json = 'output_json'         # 出力するCOCO形式JSONのパス

yolo_to_coco(yolo_annotation_dir, image_directory, output_json)
