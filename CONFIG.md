# 配置说明

## 环境变量配置

在项目根目录创建 `.env` 文件，配置以下内容：

```env
# MySQL数据库配置
DB_HOST=localhost          # 数据库主机地址
DB_PORT=3306              # 数据库端口
DB_USER=root              # 数据库用户名
DB_PASSWORD=your_password # 数据库密码
DB_NAME=your_database     # 数据库名称

# 应用配置
API_HOST=0.0.0.0          # API服务监听地址
API_PORT=8004             # API服务端口

# 模型配置
# 方式1：使用本地模型路径（推荐，离线使用）
# 将下载的模型文件夹放到项目根目录下的 models 文件夹，然后指定路径
# 例如：MODEL_PATH=models/paraphrase-multilingual-MiniLM-L12-v2
MODEL_PATH=

# 方式2：使用模型名称（如果MODEL_PATH为空，则使用此配置）
# 首次运行会从网络下载模型，后续会使用缓存
MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

## 数据库表结构

确保数据库中存在 `student_requests` 表，包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | VARCHAR(64) | 唯一标识符（主键） |
| category | VARCHAR(64) | 分类 |
| department | VARCHAR(64) | 所属院系 |
| is_overdue | VARCHAR(64) | 是否超时 |
| handling_unit | VARCHAR(64) | 受理单位 |
| receive_time | VARCHAR(64) | 受理时间 |
| finish_time | VARCHAR(64) | 完成时间 |
| processing_duration | VARCHAR(64) | 处理时长 |
| title | VARCHAR(2000) | 标题 |
| student_staff_id | VARCHAR(64) | 学号/教工号 |
| name | VARCHAR(64) | 姓名 |
| phone_number | VARCHAR(64) | 手机号 |
| contact_method | VARCHAR(64) | 联系方式 |
| status | VARCHAR(64) | 状态 |
| satisfaction | VARCHAR(64) | 满意度 |
| submit_time | VARCHAR(64) | 提交时间 |
| content | VARCHAR(2000) | 内容 |
| user_response | VARCHAR(2000) | 用户回复 |

## 时间格式说明

API接口接受的时间格式支持以下几种：

- `YYYY-MM-DD HH:MM:SS` (推荐)
- `YYYY-MM-DD HH:MM`
- `YYYY-MM-DD`
- `YYYY/MM/DD HH:MM:SS`
- `YYYY/MM/DD HH:MM`
- `YYYY/MM/DD`

示例：
```json
{
    "start_time": "2024-01-01 00:00:00",
    "end_time": "2024-12-31 23:59:59"
}
```

## 文本相似度配置

文本相似度计算使用 `sentence-transformers` 库，支持两种模型加载方式：

### 方式1：本地模型路径（推荐，离线使用）

1. **下载模型**：
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
   model.save('models/paraphrase-multilingual-MiniLM-L12-v2')
   ```
   或者从 Hugging Face 下载模型文件到本地

2. **配置路径**：
   在 `.env` 文件中设置：
   ```env
   MODEL_PATH=models/paraphrase-multilingual-MiniLM-L12-v2
   ```
   路径可以是相对路径（相对于项目根目录）或绝对路径

3. **目录结构**：
   ```
   problem-quick-response/
   ├── models/
   │   └── paraphrase-multilingual-MiniLM-L12-v2/
   │       ├── config.json
   │       ├── pytorch_model.bin
   │       └── ...
   └── ...
   ```

### 方式2：使用模型名称（在线下载）

如果 `MODEL_PATH` 为空，系统会使用 `MODEL_NAME` 配置的模型名称：
```env
MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

首次运行时会自动从网络下载模型，后续会使用缓存。

### 模型说明

- **推荐模型**：`paraphrase-multilingual-MiniLM-L12-v2`（支持中文，体积较小）
- **相似度阈值**：默认为 0.8（80%），可在 `app/services/similarity.py` 中修改

## 工作日计算

系统使用 `chinesecalendar` 库自动识别中国的法定节假日，并排除周末。

工作日计算规则：
- 排除周六、周日
- 排除中国法定节假日
- 排除调休补班（如果数据库中的日期字段包含此信息）

## 性能优化建议

1. **数据库索引**：建议在 `submit_time`、`receive_time`、`finish_time` 字段上创建索引
2. **相似度计算**：对于大量数据，相似度计算可能较慢，建议：
   - 使用更快的模型（如 `paraphrase-multilingual-MiniLM-L12-v2`）
   - 考虑异步处理或批量处理
3. **缓存**：对于相同时间范围的查询，可以考虑添加缓存机制

## 常见问题

### 1. 模型加载失败

如果sentence-transformers模型加载失败，可以：

**使用本地模型（推荐）**：
- 先在线下载模型并保存到本地
- 在 `.env` 中配置 `MODEL_PATH` 指向本地模型目录
- 确保模型目录包含完整的模型文件（config.json, pytorch_model.bin 等）

**使用在线模型**：
- 检查网络连接
- 使用国内镜像源（如配置 Hugging Face 镜像）
- 检查 `MODEL_NAME` 配置是否正确

### 2. 数据库连接失败

检查：
- 数据库服务是否启动
- `.env` 文件中的数据库配置是否正确
- 数据库用户是否有足够的权限

### 3. 时间解析错误

确保时间格式正确，或检查数据库中的时间字段是否为空或格式异常。

