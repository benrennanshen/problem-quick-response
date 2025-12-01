"""
文本相似度计算服务（使用sentence-transformers）
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# 全局模型实例（懒加载）
_model = None


def get_model():
    """
    获取sentence-transformers模型（懒加载）
    优先从本地路径加载，如果不存在则使用默认模型名
    """
    global _model
    if _model is None:
        try:
            # 从环境变量获取模型路径
            model_path = os.getenv("MODEL_PATH", "")
            
            # 如果指定了本地模型路径且路径存在，则从本地加载
            if model_path and os.path.exists(model_path):
                logger.info(f"从本地路径加载模型: {model_path}")
                _model = SentenceTransformer(model_path)
                logger.info("sentence-transformers模型加载成功（本地路径）")
            else:
                # 否则使用默认模型名（会从网络下载或使用缓存）
                default_model = os.getenv("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
                logger.info(f"使用默认模型: {default_model}")
                _model = SentenceTransformer(default_model)
                logger.info("sentence-transformers模型加载成功（默认模型）")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    return _model


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（0-1之间）
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
    
    Returns:
        相似度分数（0-1之间）
    """
    if not text1 or not text2:
        return 0.0
    
    if text1 == text2:
        return 1.0
    
    try:
        model = get_model()
        # 获取文本向量
        embeddings = model.encode([text1, text2], convert_to_numpy=True)
        
        # 计算余弦相似度
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        
        # 归一化到0-1范围（余弦相似度范围是-1到1）
        normalized_similarity = (similarity + 1) / 2
        
        return float(normalized_similarity)
    except Exception as e:
        logger.error(f"相似度计算失败: {e}")
        return 0.0


def find_duplicate_requests(requests: List[dict], similarity_threshold: float = 0.8) -> Tuple[int, List[str]]:
    """
    查找重复提交的诉求
    
    Args:
        requests: 诉求列表，每个元素包含 student_staff_id, title, content
        similarity_threshold: 相似度阈值，默认0.8
    
    Returns:
        (重复提交数量, 涉及的诉求ID列表)
    """
    if not requests:
        return 0
    
    # 按学号/教工号分组
    grouped_by_student = {}
    for req in requests:
        student_id = req.get('student_staff_id', '')
        if student_id:
            if student_id not in grouped_by_student:
                grouped_by_student[student_id] = []
            grouped_by_student[student_id].append(req)
    
    duplicate_count = 0
    processed_pairs = set()
    duplicate_ids = set()
    
    # 对每个学生的诉求进行相似度比较
    for student_id, student_requests in grouped_by_student.items():
        if len(student_requests) < 2:
            continue
        
        # 两两比较
        for i in range(len(student_requests)):
            for j in range(i + 1, len(student_requests)):
                req1 = student_requests[i]
                req2 = student_requests[j]
                
                # 组合title和content进行相似度计算
                text1 = f"{req1.get('title', '')} {req1.get('content', '')}".strip()
                text2 = f"{req2.get('title', '')} {req2.get('content', '')}".strip()
                
                if not text1 or not text2:
                    continue
                
                similarity = calculate_similarity(text1, text2)
                
                if similarity >= similarity_threshold:
                    # 避免重复计数
                    pair_key = tuple(sorted([req1.get('id', ''), req2.get('id', '')]))
                    if pair_key not in processed_pairs:
                        processed_pairs.add(pair_key)
                        duplicate_count += 1
                        duplicate_ids.update(filter(None, [req1.get('id', ''), req2.get('id', '')]))
    
    return duplicate_count, sorted(duplicate_ids)

