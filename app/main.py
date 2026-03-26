"""
FastAPI应用主入口
"""
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import io

from app.database import get_db
from app.schemas import (
    StatisticsRequest,
    StatisticsResponse,
    RequestsByIdsRequest,
    RequestsByIdsResponse,
    DetailRequest,
    DetailResponse,
    ExportRequest,
    APIResponse,
)
from app.services.statistics import StatisticsService
from app.services.excel_export import ExcelExportService

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


@app.post("/api/statistics/detail", response_model=APIResponse[DetailResponse])
async def get_detail_records(
    request: DetailRequest,
    db: Session = Depends(get_db)
):
    """
    获取明细记录（支持分页和筛选）

    - **start_time**: 开始时间，格式：YYYY-MM-DD HH:MM:SS
    - **end_time**: 结束时间，格式：YYYY-MM-DD HH:MM:SS
    - **handling_unit**: 受理单位筛选（可选）
    - **category**: 诉求分类筛选（可选）
    - **status**: 状态筛选（可选）
    - **finish_start_time**: 办结开始时间（可选）
    - **finish_end_time**: 办结结束时间（可选）
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100

    返回明细记录列表和汇总统计
    """
    try:
        logger.info(
            f"收到明细查询请求: {request.start_time} 到 {request.end_time}, "
            f"受理单位={request.handling_unit}, 分类={request.category}, "
            f"状态={request.status}, 页码={request.page}, 每页={request.page_size}"
        )

        service = StatisticsService(db)
        result = service.get_detail_records(
            start_time=request.start_time,
            end_time=request.end_time,
            handling_unit=request.handling_unit,
            category=request.category,
            status=request.status,
            finish_start_time=request.finish_start_time,
            finish_end_time=request.finish_end_time,
            page=request.page,
            page_size=request.page_size
        )

        logger.info(f"明细查询完成: 总记录数={result['total']}, 当前页记录数={len(result['records'])}")

        detail_response = DetailResponse(**result)
        return build_response(detail_response)

    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"明细查询失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.post("/api/statistics/detail/export")
async def export_detail_to_excel(
    request: ExportRequest,
    db: Session = Depends(get_db)
):
    """
    导出明细数据为 Excel 文件

    - **start_time**: 开始时间，格式：YYYY-MM-DD HH:MM:SS
    - **end_time**: 结束时间，格式：YYYY-MM-DD HH:MM:SS
    - **handling_unit**: 受理单位筛选（可选）
    - **category**: 诉求分类筛选（可选）
    - **status**: 状态筛选（可选）
    - **finish_start_time**: 办结开始时间（可选）
    - **finish_end_time**: 办结结束时间（可选）

    返回 Excel 文件流，包含两个工作表：
    - 明细数据：包含所有符合条件的记录
    - 数据汇总：包含各项统计指标
    """
    try:
        logger.info(
            f"收到导出请求: {request.start_time} 到 {request.end_time}, "
            f"受理单位={request.handling_unit}, 分类={request.category}, 状态={request.status}"
        )

        service = StatisticsService(db)
        excel_service = ExcelExportService()

        # 获取所有数据（不分页）
        result = service.get_detail_records(
            start_time=request.start_time,
            end_time=request.end_time,
            handling_unit=request.handling_unit,
            category=request.category,
            status=request.status,
            finish_start_time=request.finish_start_time,
            finish_end_time=request.finish_end_time,
            page=1,
            page_size=100000  # 设置一个很大的值以获取所有数据
        )

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"诉求明细数据_{timestamp}.xlsx"
        filename_utf8 = filename.encode('utf-8').decode('latin-1')

        # 生成 Excel 文件
        excel_bytes = excel_service.export_detail_to_excel(
            records=result['records'],
            summary=result['summary'],
            filename=filename
        )

        logger.info(f"Excel 导出成功: 文件名={filename}, 记录数={len(result['records'])}")

        # 返回文件流
        return StreamingResponse(
            io=io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename_utf8}\""
            }
        )

    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Excel 导出失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import io
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )

