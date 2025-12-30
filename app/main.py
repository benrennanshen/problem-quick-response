"""
FastAPI应用主入口
"""
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.schemas import (
    StatisticsRequest,
    StatisticsResponse,
    RequestsByIdsRequest,
    RequestsByIdsResponse,
    APIResponse,
)
from app.services.statistics import StatisticsService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 响应包装工具
def build_response(data, message: str = "success", http_code: int = 200):
    """
    统一构建响应结构
    """
    return {
        "httCode": http_code,
        "message": message,
        "data": data
    }

# 创建FastAPI应用（参考 excel-api 的方式，硬编码 root_path）
app = FastAPI(
    title="接诉即办统计系统",
    description="提供接诉即办数据的统计分析接口",
    version="1.0.0",
    root_path="/problem-quick-response",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    统一HTTP异常响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(
            data=None,
            message=str(exc.detail),
            http_code=exc.status_code
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求校验异常响应
    """
    return JSONResponse(
        status_code=422,
        content=build_response(
            data=exc.errors(),
            message="请求参数验证失败",
            http_code=422
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    未捕获异常统一处理
    """
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=build_response(
            data=None,
            message="服务器内部错误",
            http_code=500
        )
    )


@app.get("/")
async def root():
    """
    根路径，返回API信息
    """
    return build_response({
        "message": "接诉即办统计系统API",
        "version": "1.0.0",
        "docs": "/docs"
    })


@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return build_response({"status": "healthy"})


@app.post("/api/statistics", response_model=APIResponse[StatisticsResponse])
async def get_statistics(
    request: StatisticsRequest,
    db: Session = Depends(get_db)
):
    """
    获取统计数据
    
    - **start_time**: 开始时间，格式：YYYY-MM-DD HH:MM:SS
    - **end_time**: 结束时间，格式：YYYY-MM-DD HH:MM:SS
    
    返回统计指标：
    - 数据总量
    - 受理量和受理率
    - 办结量和办结率
    - 不同时间段的办结数量
    - 平均办结时间
    - 重复提交数量
    """
    try:
        logger.info(f"收到统计请求: {request.start_time} 到 {request.end_time}")
        
        service = StatisticsService(db)
        result = service.calculate_statistics(
            start_time=request.start_time,
            end_time=request.end_time
        )
        
        logger.info(f"统计计算完成: 总记录数={result['total_count']}")
        
        statistics = StatisticsResponse(**result)
        return build_response(statistics)
        
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"统计计算失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.post("/api/requests/by-ids", response_model=APIResponse[RequestsByIdsResponse])
async def get_requests_by_ids(
    request: RequestsByIdsRequest,
    db: Session = Depends(get_db)
):
    """
    根据ID列表获取诉求详细信息
    """
    if not request.ids:
        raise HTTPException(status_code=400, detail="ids不能为空")

    try:
        service = StatisticsService(db)
        records = service.get_requests_by_ids(request.ids)
        response_data = RequestsByIdsResponse(requests=records)
        return build_response(response_data)
    except Exception as e:
        logger.error(f"根据ID获取诉求失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )

