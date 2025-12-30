FROM python:3.11-slim-bookworm

# 切换到阿里云 Debian 12 源以加速依赖安装
RUN echo "Types: deb\nURIs: https://mirrors.aliyun.com/debian\nSuites: bookworm bookworm-updates\nComponents: main\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\n\nTypes: deb\nURIs: https://mirrors.aliyun.com/debian-security\nSuites: bookworm-security\nComponents: main\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg" > /etc/apt/sources.list.d/debian.sources

WORKDIR /app

# 安装必要的系统依赖（最小化）
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 先安装本地下载好的 PyTorch CPU 轮子，再安装其余依赖
COPY torch-2.2.1+cpu-cp311-cp311-linux_x86_64.whl ./
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch-2.2.1+cpu-cp311-cp311-linux_x86_64.whl \
    && pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip cache purge \
    && rm -rf /root/.cache/pip

# 只复制必要的应用文件（模型文件通过volume挂载）
COPY app/ ./app/
COPY *.py ./
COPY *.md ./
COPY *.txt ./

# 清理Python缓存
RUN find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true \
    && find . -type f -name "*.pyc" -delete \
    && find . -type f -name "*.pyo" -delete

# 设置环境变量（将Hugging Face缓存放在临时目录以减少体积）
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_OFFLINE=0 \
    HF_HOME=/tmp/.cache/huggingface

EXPOSE 8004

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]

