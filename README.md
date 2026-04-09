# 接诉即办统计系统

基于FastAPI的接诉即办数据统计分析系统，提供完整的数据统计和分析功能。

## 部署说明（重要）

### 一键部署

```powershell
# 在项目根目录执行
.\deploy.ps1
```

**首次部署需要约 4 分钟**（下载依赖），后续代码变更只需 **5 秒**。

### 部署架构

- **本机（Windows）**: 执行 deploy.ps1，通过远程 Docker 构建
- **远程服务器（192.168.1.10）**: Docker Host，运行容器
- **Docker 镜像**: 分层缓存，PyTorch 和依赖包缓存在基础镜像中

### 文件说明

| 文件 | 说明 |
|------|------|
| `deploy.ps1` | 一键部署脚本，构建镜像并远程部署 |
| `Dockerfile` | 应用镜像，基于基础镜像，只包含代码 |
| `Dockerfile.base` | 基础镜像，包含 PyTorch 和所有依赖 |
| `docker-compose.yml` | 远程服务器上的容器编排配置 |

### 依赖变更时重建基础镜像

如果修改了 `requirements.txt`，需要先重建基础镜像：

```powershell
# 重建基础镜像（耗时约 4 分钟）
docker build -f Dockerfile.base -t problemquickresponse:base .

# 然后正常部署
.\deploy.ps1
```

### 部署参数配置

在 `deploy.ps1` 中可配置：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `ImageName` | problemquickresponse | 镜像名称 |
| `ImageTag` | latest | 镜像标签 |
| `DockerHost` | 192.168.1.10:2375 | 远程 Docker 地址 |
| `RemoteHost` | 192.168.1.10 | 远程服务器地址 |
| `RemoteUser` | root | SSH 用户 |
| `RemoteProjectPath` | /fskj/workspace/problemquickresponse | 远程项目路径 |

## 功能特性

- 📊 数据统计：支持按时间范围查询统计数据
- 📈 多维度分析：受理率、办结率、平均办结时间等
- 🕐 工作日计算：自动过滤节假日和周末
- 🔍 重复检测：基于文本相似度的重复提交识别
- 🚀 高性能：使用sentence-transformers进行高效的文本相似度计算

## 技术栈

- **Python**: 3.11
- **Web框架**: FastAPI
- **数据库**: MySQL (SQLAlchemy ORM)
- **文本相似度**: sentence-transformers
- **日期处理**: chinesecalendar
- **AI 模型**: PyTorch 2.2.1 CPU
- **容器**: Docker + Docker Compose

## 项目结构

```
problem-quick-response/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models.py            # 数据库模型
│   ├── schemas.py           # Pydantic数据验证模型
│   ├── database.py          # 数据库连接配置
│   ├── services/
│   │   ├── __init__.py
│   │   ├── statistics.py    # 统计计算服务
│   │   └── similarity.py    # 文本相似度计算
│   └── utils/
│       ├── __init__.py
│       └── date_utils.py    # 日期工具（过滤节假日和周末）
├── requirements.txt         # 依赖包
├── .env                     # 环境变量配置（需要创建）
└── README.md               # 项目说明
```

## 安装步骤

### 本地开发

#### 1. 克隆项目

```bash
git clone <repository-url>
cd problem-quick-response
```

#### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

创建 `.env` 文件：

```env
# MySQL数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database_name

# 应用配置
API_HOST=0.0.0.0
API_PORT=8004

# 模型配置（二选一）
# 方式1：使用本地模型路径（推荐，离线使用）
MODEL_PATH=models/paraphrase-multilingual-MiniLM-L12-v2

# 方式2：使用模型名称（如果MODEL_PATH为空，则使用此配置）
MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

#### 5. 准备模型文件（可选，推荐）

如果使用本地模型（离线使用），需要先下载模型：

```python
from sentence_transformers import SentenceTransformer

# 下载并保存模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
model.save('./models/paraphrase-multilingual-MiniLM-L12-v2')
```

### 生产部署（Docker）

参见上方「部署说明」章节，使用 `.\deploy.ps1` 一键部署。

## 运行项目

### 本地开发模式

```bash
python -m app.main
```

或使用uvicorn：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### 生产部署模式

```powershell
# Windows 本机执行，自动部署到远程服务器
.\deploy.ps1
```

## API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8004/problem-quick-response/docs
- ReDoc: http://localhost:8004/problem-quick-response/redoc

## API接口

### 获取统计数据

**POST** `/api/statistics`

**请求体：**
```json
{
    "start_time": "2024-01-01 00:00:00",
    "end_time": "2024-12-31 23:59:59"
}
```

**响应：**
```json
{
    "total_count": 1000,
    "accepted_count": 950,
    "acceptance_rate": 0.95,
    "completed_count": 900,
    "completion_rate": 0.90,
    "completed_in_one_workday": 200,
    "completed_in_3_days": 400,
    "completed_in_7_days": 600,
    "completed_over_7_days": 300,
    "over_7_days_completion_rate": 0.30,
    "average_completion_hours": 48.5,
    "duplicate_submissions": 50
}
```

## 统计指标说明

- **total_count**: 数据总量（指定时间范围内的记录数）
- **accepted_count**: 受理量（有受理时间的记录数）
- **acceptance_rate**: 受理率（受理量/数据总量）
- **completed_count**: 办结量（有完成时间的记录数）
- **completion_rate**: 办结率（办结量/数据总量）
- **completed_in_one_workday**: 一个工作日办结数量
- **completed_in_3_days**: 3个工作日内办结数量
- **completed_in_7_days**: 7个工作日内办结数量
- **completed_over_7_days**: 超过7个工作日办结数量
- **over_7_days_completion_rate**: 超过7天后的办结率
- **average_completion_hours**: 平均办结时间（小时，已过滤节假日和周末）
- **duplicate_submissions**: 重复提交数量（同一人，文本相似度>80%）

## 注意事项

1. **时间格式**：支持多种时间格式，推荐使用 `YYYY-MM-DD HH:MM:SS`
2. **工作日计算**：自动排除周末和中国的法定节假日
3. **文本相似度模型**：
   - **推荐**：使用本地模型（配置 `MODEL_PATH`），离线可用，加载更快
   - **备选**：使用在线模型（配置 `MODEL_NAME`），首次运行需要网络下载
   - 模型文件约 400MB，确保有足够磁盘空间
4. **数据库连接**：确保MySQL数据库可访问，且表结构符合要求

## 开发说明

### 数据库表结构

项目使用 `student_requests` 表，包含以下关键字段：
- `id`: 唯一标识符
- `student_staff_id`: 学号/教工号
- `title`: 标题
- `content`: 内容
- `submit_time`: 提交时间
- `receive_time`: 受理时间
- `finish_time`: 完成时间
- `status`: 状态

### 自定义配置

- **相似度阈值**：在 `app/services/similarity.py` 中可调整 `similarity_threshold`（默认0.8）
- **模型选择**：在 `app/services/similarity.py` 中可更换sentence-transformers模型

## 许可证

MIT License

