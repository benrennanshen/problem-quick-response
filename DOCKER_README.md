# problem-quick-response Docker 部署指南

本文档参考 `g:\excelapi` 项目的 Docker 方案，介绍如何将本项目打包成镜像并在目标主机运行。

## 📋 前置要求
- Docker 20.0+
- 可访问 `https://mirrors.aliyun.com`（若网络受限，可自行修改 `Dockerfile` 的源）

## 🚀 快速开始
```powershell
# （可选）设置代理与远程 Docker 主机
$env:HTTP_PROXY="http://192.168.1.198:10811"
$env:HTTPS_PROXY="http://192.168.1.198:10811"
$env:DOCKER_HOST="tcp://192.168.1.10:2375"

# 1. 构建镜像
docker build -t problemquickresponse:latest .

# 2. 启动容器（映射 8004 端口，挂载日志与模型目录，可载入 .env）
docker run -d `
  --name pqr-api `
  -p 8004:8004 `
  --env-file .env `
  -v ${PWD}/logs:/app/logs `
  -v ${PWD}/models:/app/models `
  problemquickresponse:latest

# 3. 查看实时日志
docker logs -f pqr-api

# 4. 停止并删除容器
docker stop pqr-api && docker rm pqr-api
```

## 🌐 对外访问
- API 根地址：`http://<host>:8004`
- Swagger 文档：`http://<host>:8004/problem-quick-response/docs`
- ReDoc：`http://<host>:8004/problem-quick-response/redoc`

## 📁 关键文件说明
- `Dockerfile`：基于 `python:3.11-slim-bookworm`，使用阿里云 apt 源与清华 PyPI 源安装依赖，运行 `uvicorn app.main:app --port 8004`。
- `.dockerignore`：排除虚拟环境、`__pycache__`、日志、`models/`、`env/` 等文件，避免镜像体积膨胀。
- `requirements.txt`：项目依赖清单。

## ⚙️ 配置要点
- 环境变量：镜像中默认 `PYTHONPATH=/app`、`PYTHONUNBUFFERED=1`。
- 监听端口：容器内 `8004`，可通过 `-p 宿主端口:8004` 调整暴露端口。
- 静态模型：`models/` 目录被构建时忽略，需要通过 `-v ${PWD}/models:/app/models` 挂载到容器。
- 日志与数据：示例挂载 `./logs:/app/logs`，可按需追加其他卷。
- 环境配置：请将 `env.example` 复制为 `.env` 并补齐实际配置，运行容器时使用 `--env-file .env` 注入。

## 🧩 常见问题
1. **构建卡在 apt**：确认能访问阿里云源，或换回官方源。
2. **端口冲突**：启动前检查宿主 8004 端口 `netstat -ano | findstr 8004`。
3. **依赖安装慢**：可在构建时加 `--network host` 或使用公司内源。
4. **访问路径 404**：接口文档被挂在 `/problem-quick-response/*`，务必带上该前缀。

## 🔐 建议
- 生产环境可搭配 Nginx/Traefik 做反向代理与 HTTPS。
- 定期执行 `docker system prune` 清理无用资源。
- 若追求更小体积，可改用多阶段构建或 `python:3.11-slim` 基础镜像。

需要扩展 Compose、K8s 或其他部署方式，可继续告诉我。

