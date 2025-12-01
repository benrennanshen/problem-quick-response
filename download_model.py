"""
下载 sentence-transformers 模型到本地
"""
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 模型配置
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
MODEL_DIR = Path("models") / MODEL_NAME

def download_model():
    """
    下载模型到本地
    """
    print(f"开始下载模型: {MODEL_NAME}")
    print("这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 创建模型目录
        MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
        
        # 下载模型
        print("正在从网络下载模型...")
        model = SentenceTransformer(MODEL_NAME)
        
        # 保存到本地
        print(f"正在保存模型到: {MODEL_DIR}")
        model.save(str(MODEL_DIR))
        
        print(f"\n✅ 模型下载完成！")
        print(f"模型保存路径: {MODEL_DIR.absolute()}")
        print(f"\n请在 .env 文件中配置:")
        print(f"MODEL_PATH={MODEL_DIR}")
        
    except Exception as e:
        print(f"\n❌ 模型下载失败: {e}")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 使用代理或VPN")
        print("3. 配置 Hugging Face 镜像源")
        raise

if __name__ == "__main__":
    download_model()

