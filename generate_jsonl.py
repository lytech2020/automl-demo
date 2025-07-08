import os
import json
from PIL import Image
import random
from datetime import datetime, timedelta

# 本地图片文件夹
image_folder = './boiler0709'

# AzureML 路径前缀
azureml_prefix = 'azureml://subscriptions/4e3d915a-bc68-42e8-8bc1-af28dd4f8d91/resourcegroups/lytech-rg/workspaces/lytech-machine-learning-workspace/datastores/workspaceblobstore/paths/UI/2025-07-08_093621_UTC/boiler0709'

# 输出文件路径
output_path = 'boiler_dataset_detailed.jsonl'

# 模拟起始时间
base_time = datetime(2025, 6, 29, 14, 0, 0)

# 获取所有 jpg 文件
image_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith('.jpg')])

# 写入 JSONL 文件
with open(output_path, 'w', encoding='utf-8') as outfile:
    for i, filename in enumerate(image_files):
        file_path = os.path.join(image_folder, filename)
        label = ''.join([c for c in filename if not c.isdigit()]).replace('.jpg', '')
        image_url = f"{azureml_prefix}/{filename}"
        relative_path = f"{label}/{filename}"

        # 打开图像获取尺寸
        with Image.open(file_path) as img:
            width, height = img.size

        # 随机生成温度值
        temperature_value = round(random.uniform(120.0, 320.0), 1)

        # 模拟时间戳
        timestamp = (base_time + timedelta(minutes=i * 5)).strftime('%Y-%m-%d %H:%M:%S')

        record = {
            "image_url": image_url,
            "image_details": {
                "format": "jpg",
                "width": f"{width}px",
                "height": f"{height}px"
            },
            "label": label,
            "temperature_value": str(temperature_value),
            "timestamp": timestamp,
            "relative_path": relative_path
        }

        outfile.write(json.dumps(record, ensure_ascii=False) + '\n')

print(f"✅ JSONL 文件生成完成：{output_path}")
