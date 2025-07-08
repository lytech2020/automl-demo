# Azure ML 使用指南

本指南介绍如何使用Azure CLI ML来训练锅炉温度分类模型。

## 配置文件说明

### 1. 基础训练配置 (`train.yml`)
- 使用CPU计算资源
- 适合快速原型开发和测试
- 使用scikit-learn环境

### 2. 高级训练配置 (`train_advanced.yml`)
- 支持参数化配置
- 可以通过命令行覆盖默认参数
- 适合超参数调优

### 3. GPU训练配置 (`train_gpu.yml`)
- 使用GPU计算资源
- 适合深度学习模型
- 使用PyTorch环境

## 使用步骤

### 1. 安装Azure CLI ML扩展

```bash
# 安装Azure CLI ML扩展
az extension add -n ml

# 或者更新现有扩展
az extension update -n ml
```

### 2. 登录Azure

```bash
az login
```

### 3. 设置工作区

```bash
# 设置默认资源组和工作区
az configure --defaults group=<your-resource-group> workspace=<your-workspace>

# 或者使用完整路径
az ml workspace show --resource-group <your-resource-group> --name <your-workspace>
```

### 4. 上传数据

```bash
# 上传JSONL文件到数据存储
az ml data create --name boiler-dataset --path boiler_dataset_with_dimensions.jsonl --type uri_file

# 或者上传整个目录
az ml data create --name boiler-dataset-folder --path . --type uri_folder
```

### 5. 提交训练作业

#### 基础训练
```bash
az ml job create --file train.yml
```

#### 高级训练（自定义参数）
```bash
az ml job create --file train_advanced.yml \
  --set inputs.epochs=20 \
  --set inputs.batch_size=64 \
  --set inputs.learning_rate=0.0005 \
  --set inputs.model_type=gradient_boosting
```

#### GPU训练
```bash
az ml job create --file train_gpu.yml
```

### 6. 监控训练进度

```bash
# 查看作业状态
az ml job show --name <job-name>

# 查看作业日志
az ml job stream --name <job-name>

# 列出所有作业
az ml job list --query "[].{Name:name, Status:status, Created:creation_context.created_at}"
```

### 7. 下载模型和结果

```bash
# 下载模型
az ml job download --name <job-name> --output-name model_output --download-path ./models

# 查看指标
az ml job show --name <job-name> --query "outputs.model_output"
```

## 配置文件自定义

### 修改计算资源
```yaml
# 使用不同的计算集群
compute: azureml:my-custom-cluster

# 或者使用自动缩放
compute: azureml:auto-scale-cluster
```

### 修改环境
```yaml
# 使用自定义环境
environment: azureml:my-custom-env@latest

# 或者使用特定版本
environment: azureml:AzureML-sklearn-1.1-ubuntu20.04-py38-cpu@1.0.0
```

### 添加更多输入参数
```yaml
inputs:
  data_path:
    type: uri_folder
    path: azureml://datastores/workspaceblobstore/paths/boiler_dataset/
  validation_split:
    type: number
    default: 0.2
  random_seed:
    type: integer
    default: 42
```

## 最佳实践

### 1. 配置文件命名
- 使用描述性的名称：`train_boiler_classification.yml`
- 包含版本信息：`train_v1.0.yml`
- 区分环境：`train_prod.yml`, `train_dev.yml`

### 2. 参数化配置
- 将经常变化的参数设为输入
- 使用合理的默认值
- 添加参数验证

### 3. 资源管理
- 根据模型复杂度选择计算资源
- 使用标签管理作业
- 定期清理旧的作业和模型

### 4. 监控和日志
- 记录关键指标
- 保存模型版本
- 跟踪实验历史

## 故障排除

### 常见问题

1. **作业失败**
   ```bash
   # 查看详细错误信息
   az ml job show --name <job-name> --query "errors"
   ```

2. **计算资源不足**
   ```bash
   # 检查计算集群状态
   az ml compute show --name <cluster-name>
   ```

3. **数据路径错误**
   ```bash
   # 验证数据存储
   az ml datastore show --name <datastore-name>
   ```

### 调试技巧

1. **本地测试**
   ```bash
   # 在本地运行训练脚本
   python train.py --data-path ./boiler_dataset --output-dir ./output
   ```

2. **查看日志**
   ```bash
   # 实时查看日志
   az ml job stream --name <job-name> --follow
   ```

3. **检查环境**
   ```bash
   # 验证环境配置
   az ml environment show --name <environment-name>
   ```

## 示例工作流

```bash
# 1. 准备数据
python3 gen.py --output boiler_dataset.jsonl --verbose

# 2. 上传数据
az ml data create --name boiler-dataset --path boiler_dataset.jsonl --type uri_file

# 3. 提交训练作业
az ml job create --file train.yml

# 4. 监控进度
az ml job stream --name <job-name>

# 5. 下载结果
az ml job download --name <job-name> --output-name model_output --download-path ./models
```

这样你就可以灵活地使用不同的配置文件来训练你的模型了！ 