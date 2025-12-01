# 模型目录说明

此目录用于存放 sentence-transformers 模型文件。

## 使用方法

### 1. 下载模型

使用 Python 脚本下载模型：

```python
from sentence_transformers import SentenceTransformer

# 下载模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 保存到本地
model.save('./models/paraphrase-multilingual-MiniLM-L12-v2')
```

或者从 Hugging Face 手动下载：
- 访问：https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- 下载所有文件到 `models/paraphrase-multilingual-MiniLM-L12-v2/` 目录

### 2. 目录结构

下载后的目录结构应该是：

```
models/
└── paraphrase-multilingual-MiniLM-L12-v2/
    ├── config.json
    ├── pytorch_model.bin
    ├── tokenizer_config.json
    ├── vocab.txt
    └── modules.json
```

### 3. 配置环境变量

在 `.env` 文件中配置：

```env
MODEL_PATH=models/paraphrase-multilingual-MiniLM-L12-v2
```

### 4. 验证

启动应用后，查看日志应该显示：
```
从本地路径加载模型: models/paraphrase-multilingual-MiniLM-L12-v2
sentence-transformers模型加载成功（本地路径）
```

## 注意事项

1. 模型文件较大（约 400MB），确保有足够的磁盘空间
2. 模型路径可以是相对路径（相对于项目根目录）或绝对路径
3. 如果 `MODEL_PATH` 配置的路径不存在，系统会自动回退到使用 `MODEL_NAME` 在线下载

