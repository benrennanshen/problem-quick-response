"""
Pydantic数据验证模型
"""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


T = TypeVar("T")


class APIResponse(GenericModel, Generic[T]):
    """
    通用API响应包装
    """
    httCode: int = Field(..., description="HTTP状态码")
    message: str = Field(..., description="提示信息")
    data: T = Field(..., description="后端返回的数据内容")


class StatisticsRequest(BaseModel):
    """
    统计请求模型
    """
    start_time: str = Field(..., description="开始时间，格式：YYYY-MM-DD HH:MM:SS")
    end_time: str = Field(..., description="结束时间，格式：YYYY-MM-DD HH:MM:SS")

class DepartmentStatistics(BaseModel):
    """
    部门受理及办结统计
    """
    handling_unit: str = Field(..., description="受理单位")
    total_count: int = Field(..., description="总件数")
    accepted_count: int = Field(..., description="受理量")
    completed_count: int = Field(..., description="办结量")
    completed_in_one_workday: int = Field(..., description="1个工作日内办结数量")
    completed_in_3_days: int = Field(..., description="3个工作日内办结数量（排除1日内）")
    completed_in_7_days: int = Field(..., description="7个工作日内办结数量（排除1日/3日内）")
    completed_over_7_days: int = Field(..., description="超过7个工作日办结数量")
    duplicate_submissions: int = Field(..., description="重复提交数量（仅统计该受理单位）")
    duplicate_submission_ids: str = Field(..., description="重复提交记录ID（该受理单位），英文逗号分隔")

class CategoryStatistics(BaseModel):
    """
    诉求分类统计
    """
    category: str = Field(..., description="诉求分类")
    total_count: int = Field(..., description="本期开受理量")
    percentage: str = Field(..., description="占比（百分比字符串）")
    issues_summary: str = Field(..., description="问题汇总，按1/2/3...拼接的content")


class StatisticsResponse(BaseModel):
    """
    统计响应模型
    """
    total_count: int = Field(..., description="数据总量")
    accepted_count: int = Field(..., description="受理量")
    acceptance_rate: str = Field(..., description="受理率（百分比字符串）")
    completed_count: int = Field(..., description="办结量")
    completion_rate: str = Field(..., description="办结率（百分比字符串）")
    completed_in_one_workday: int = Field(..., description="一个工作日办结数量")
    completed_in_one_workday_ids: str = Field(..., description="一个工作日办结的记录ID，英文逗号分隔")
    completed_in_3_days: int = Field(..., description="3天内办结数量")
    completed_in_3_days_ids: str = Field(..., description="3天内办结的记录ID，英文逗号分隔")
    completed_in_7_days: int = Field(..., description="7天内办结数量")
    completed_in_7_days_ids: str = Field(..., description="7天内办结的记录ID，英文逗号分隔")
    completed_over_7_days: int = Field(..., description="超期7天后办结数量")
    completed_over_7_days_ids: str = Field(..., description="超期7天后办结的记录ID，英文逗号分隔")
    over_7_days_completion_rate: str = Field(..., description="超过7天后的办结率（百分比字符串）")
    average_completion_hours: str = Field(..., description="平均办结时间（小时字符串，带单位）")
    duplicate_submissions: int = Field(..., description="重复提交数量")
    duplicate_submission_ids: str = Field(..., description="重复提交的记录ID，英文逗号分隔")
    department_statistics: List[DepartmentStatistics] = Field(
        ..., description="按受理单位汇总的办结统计"
    )
    category_statistics: List[CategoryStatistics] = Field(
        ..., description="诉求分类统计信息"
    )


class StudentRequestItem(BaseModel):
    """
    学生诉求记录
    """
    诉求ID: str
    诉求分类: Optional[str] = None
    所属院系: Optional[str] = None
    是否超时: Optional[str] = None
    受理单位: Optional[str] = None
    受理时间: Optional[str] = None
    完成时间: Optional[str] = None
    处理时长: Optional[str] = None
    标题: Optional[str] = None
    学号_教工号: Optional[str] = Field(None, alias="学号/教工号")
    姓名: Optional[str] = None
    手机号: Optional[str] = None
    联系方式: Optional[str] = None
    状态: Optional[str] = None
    满意度: Optional[str] = None
    提交时间: Optional[str] = None
    内容: Optional[str] = None
    用户回复: Optional[str] = None


class RequestsByIdsRequest(BaseModel):
    ids: List[str] = Field(..., description="诉求ID列表")


class RequestsByIdsResponse(BaseModel):
    requests: List[StudentRequestItem]

