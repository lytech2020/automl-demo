# AutoML Demo - JSON/JSONL Tools

这个项目包含两个主要工具：
1. **JSON to JSONL Converter** - 将JSON文件转换为JSONL格式
2. **Boiler Dataset Generator** - 从锅炉数据集生成JSONL文件

## 工具概览

### 1. JSON to JSONL Converter (`json2jsonl.py`)
一个功能强大的JSON到JSONL（JSON Lines）格式转换脚本。

## 功能特性

- 支持多种JSON输入格式：
  - 单个JSON对象
  - JSON对象数组
  - 多个JSON对象（每行一个）
  - 多个JSON对象（连续排列）
- 支持压缩和美化输出格式
- 完整的错误处理和用户友好的提示
- 支持UTF-8编码

## 安装要求

- Python 3.6+
- **Pillow库**（用于读取图片尺寸）：`pip install Pillow`
- 其他依赖包：无需额外依赖

## 使用方法

### 基本用法

```bash
python3 json2jsonl.py input.json output.jsonl
```

### 美化输出

```bash
python3 json2jsonl.py input.json output.jsonl --pretty
```

### 自定义缩进

```bash
python3 json2jsonl.py input.json output.jsonl --pretty --indent 4
```

### 详细输出

```bash
python3 json2jsonl.py input.json output.jsonl --verbose
```

## 命令行参数

- `input`: 输入JSON文件路径
- `output`: 输出JSONL文件路径
- `--pretty`: 美化输出格式（每个JSON对象占多行）
- `--indent`: 缩进级别（默认：2，仅在--pretty模式下有效）
- `--verbose, -v`: 显示详细处理信息

## 示例

### 输入文件 (example.json)
```json
{
    "image_url": "azureml://subscriptions/<my-subscription-id>/resourcegroups/<my-resource-group>/workspaces/<my-workspace>/datastores/<my-datastore>/paths/image_data/Image_01.png",
    "image_details": {
        "format": "png",
        "width": "2230px",
        "height": "4356px"
    },
    "label": "cat"
}
{
    "image_url": "azureml://subscriptions/<my-subscription-id>/resourcegroups/<my-resource-group>/workspaces/<my-workspace>/datastores/<my-datastore>/paths/image_data/Image_02.jpeg",
    "image_details": {
        "format": "jpeg",
        "width": "3456px",
        "height": "3467px"
    },
    "label": "dog"
}
```

### 转换命令
```bash
python3 json2jsonl.py example.json output.jsonl
```

### 输出文件 (output.jsonl)
```
{"image_url":"azureml://subscriptions/<my-subscription-id>/resourcegroups/<my-resource-group>/workspaces/<my-workspace>/datastores/<my-datastore>/paths/image_data/Image_01.png","image_details":{"format":"png","width":"2230px","height":"4356px"},"label":"cat"}
{"image_url":"azureml://subscriptions/<my-subscription-id>/resourcegroups/<my-resource-group>/workspaces/<my-workspace>/datastores/<my-datastore>/paths/image_data/Image_02.jpeg","image_details":{"format":"jpeg","width":"3456px","height":"3467px"},"label":"dog"}
```

## 支持的输入格式

1. **单个JSON对象**：
   ```json
   {"key": "value"}
   ```

2. **JSON对象数组**：
   ```json
   [{"key1": "value1"}, {"key2": "value2"}]
   ```

3. **每行一个JSON对象**：
   ```json
   {"key1": "value1"}
   {"key2": "value2"}
   ```

4. **连续排列的JSON对象**：
   ```json
   {"key1": "value1"}{"key2": "value2"}
   ```

## 错误处理

脚本包含完整的错误处理机制：
- 文件不存在时的友好提示
- JSON解析错误的处理
- 输出文件写入错误的处理
- 详细的错误信息输出

## 2. Boiler Dataset Generator (`gen.py`)

一个专门用于生成锅炉数据集JSONL文件的脚本，支持从CSV标签文件读取标签信息。

### 功能特性

- 自动扫描boiler_dataset目录下的所有图片文件
- 从CSV文件读取温度分类标签信息
- 生成符合Azure ML格式的image_url
- **自动读取图片实际尺寸**（需要安装Pillow库）
- 支持压缩和美化输出格式
- 提供详细的统计信息

### 使用方法

#### 基本用法
```bash
python3 gen.py --output boiler_dataset.jsonl
```

#### 美化输出
```bash
python3 gen.py --output boiler_dataset.jsonl --pretty
```

#### 详细输出
```bash
python3 gen.py --output boiler_dataset.jsonl --verbose
```

#### 自定义参数
```bash
python3 gen.py --output boiler_dataset.jsonl \
  --dataset-dir boiler_dataset \
  --csv-file boiler_dataset/boiler_labels_100.csv \
  --base-url "custom://base/path/" \
  --pretty --verbose
```

### 命令行参数

- `--output`: 输出JSONL文件路径（必需）
- `--dataset-dir`: 数据集目录路径（默认：boiler_dataset）
- `--csv-file`: 包含标签的CSV文件（默认：boiler_dataset/boiler_labels_100.csv）
- `--base-url`: 图片路径的基础URL
- `--pretty`: 美化输出格式
- `--verbose, -v`: 显示详细处理信息

### 输出格式

生成的JSONL文件包含以下字段：
- `image_url`: 完整的Azure ML图片URL
- `image_details`: 图片详细信息（格式、尺寸等）
- `label`: 温度分类标签（低温、中温、高温、极高温）
- `temperature_value`: 具体温度值
- `timestamp`: 时间戳
- `relative_path`: 相对路径

### 示例输出

```json
{
  "image_url": "azureml://subscriptions/4e3d915a-bc68-42e8-8bc1-af28dd4f8d91/resourcegroups/lytech-rg/workspaces/lytech-machine-learning-workspace/datastores/workspaceblobstore/paths/LocalUpload/aeafb12c43181b9788690d5db006e885/boiler_dataset/高温/boiler_autoML_03.png",
  "image_details": {
    "format": "png",
    "width": "612px",
    "height": "459px"
  },
  "label": "高温",
  "temperature_value": "903.0",
  "timestamp": "2025-06-08 02:03:13",
  "relative_path": "高温/boiler_autoML_03.png"
}
```

**注意**：如果未安装Pillow库，图片尺寸将显示为"unknownpx"。

## 许可证

MIT License