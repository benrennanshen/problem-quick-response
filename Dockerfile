# 使用基础镜像（包含 PyTorch 和所有依赖）
FROM problemquickresponse:base

WORKDIR /app

# 只复制应用代码（这一层变化快，但很小）
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
