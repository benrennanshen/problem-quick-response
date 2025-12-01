# Docker 镜像优化说明

## 优化内容

### 1. 使用 PyTorch CPU 专用版本
- **原问题**：`torch==2.2.1` 完整版本包含 CUDA 支持，体积约 2-3GB
- **优化方案**：使用 `torch==2.2.1+cpu`，体积减少约 60-70%（约 800MB-1GB）
- **实现**：在 Dockerfile 中单独从 PyTorch 官方源安装 CPU 版本

### 2. 清理构建缓存
- 清理 pip 缓存：`pip cache purge`
- 清理 apt 缓存：`rm -rf /var/lib/apt/lists/*`
- 清理 Python 编译文件：`__pycache__`、`*.pyc`、`*.pyo`

### 3. 优化文件复制
- 通过 `.dockerignore` 排除模型文件（`models/`）
- 模型文件通过 Docker volume 挂载，不包含在镜像中
- 排除不必要的文件（`.git`、日志、临时文件等）

### 4. 环境变量优化
- 设置 `HF_HOME=/tmp/.cache/huggingface` 将 Hugging Face 缓存放在临时目录

## 使用方法

### 构建镜像
```bash
docker build -t problem-quick-response:latest .
```

### 运行容器（挂载模型文件）
```bash
docker run -d \
  -p 8004:8004 \
  -v $(pwd)/models:/app/models \
  -e MODEL_PATH=/app/models/paraphrase-multilingual-MiniLM-L12-v2 \
  problem-quick-response:latest
```

### 使用 docker-compose（推荐）
创建 `docker-compose.yml`：
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8004:8004"
    volumes:
      - ./models:/app/models
    environment:
      - MODEL_PATH=/app/models/paraphrase-multilingual-MiniLM-L12-v2
    restart: unless-stopped
```

## 预期效果

- **优化前**：镜像体积约 5GB+
- **优化后**：镜像体积约 1.5-2GB（减少 60-70%）

## 进一步优化建议

如果镜像体积仍然较大，可以考虑：

1. **使用 Alpine 基础镜像**（不推荐，可能有兼容性问题）
   ```dockerfile
   FROM python:3.11-alpine
   ```

2. **多阶段构建**：在构建阶段安装依赖，运行时阶段只复制必要文件

3. **使用更小的模型**：如果业务允许，使用更小的 sentence-transformers 模型

4. **压缩模型文件**：使用量化或压缩技术减小模型文件大小

## 注意事项

1. **模型文件挂载**：确保在运行容器时挂载模型目录，否则应用无法加载模型
2. **CPU 版本限制**：使用 CPU 版本的 PyTorch，无法使用 GPU 加速
3. **首次运行**：如果模型文件不存在，应用会尝试从网络下载（需要网络连接）

