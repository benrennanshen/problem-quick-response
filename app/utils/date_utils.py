"""
日期工具类：处理工作日计算，过滤节假日和周末
"""
import chinese_calendar 
from datetime import datetime, timedelta
from typing import List, Tuple


def parse_datetime(date_str: str) -> datetime:
    """
    解析日期字符串，支持多种格式
    如果只传日期（没有时分秒），会根据上下文自动补全：
    - 作为开始时间：补全为 00:00:00
    - 作为结束时间：补全为 23:59:59
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    raise ValueError(f"无法解析日期格式: {date_str}")


def normalize_time_range(start_time: str, end_time: str) -> tuple:
    """
    规范化时间范围，自动补全时分秒

    规则：
    - 如果 start_time 只包含日期（没有时分秒），自动补全为 00:00:00
    - 如果 end_time 只包含日期（没有时分秒），自动补全为 23:59:59
    - 如果已包含时分秒，保持原值不变

    Args:
        start_time: 开始时间字符串
        end_time: 结束时间字符串

    Returns:
        (start_datetime, end_datetime): 规范化后的 datetime 对象

    Examples:
        normalize_time_range("2024-01-01", "2024-01-01")
        -> (2024-01-01 00:00:00, 2024-01-01 23:59:59)

        normalize_time_range("2024-01-01 08:30:00", "2024-01-01 17:30:00")
        -> (2024-01-01 08:30:00, 2024-01-01 17:30:00)  # 保持原值
    """
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)

    # 检查原始字符串是否包含时分秒（通过冒号判断）
    start_has_time = ":" in start_time
    end_has_time = ":" in end_time

    # 如果开始时间只传了日期，补全为 00:00:00
    if not start_has_time:
        start_dt = datetime.combine(start_dt.date(), datetime.min.time())

    # 如果结束时间只传了日期，补全为 23:59:59
    if not end_has_time:
        end_dt = datetime.combine(end_dt.date(), datetime.max.time().replace(microsecond=0))

    return start_dt, end_dt


def is_workday(date: datetime) -> bool:
    """
    判断是否为工作日（排除周末和节假日）
    """
    return chinese_calendar.is_workday(date.date())


def get_workdays_between(start: datetime, end: datetime) -> int:
    """
    计算两个日期之间的工作日数量（不包括结束日期）
    """
    if start >= end:
        return 0
    
    workdays = 0
    current = start.date()
    end_date = end.date()
    
    while current < end_date:
        if chinese_calendar.is_workday(current):
            workdays += 1
        current += timedelta(days=1)
    
    return workdays


def get_workday_hours_between(start: datetime, end: datetime) -> float:
    """
    计算两个日期之间的工作小时数（排除周末和节假日）
    如果跨多个工作日，只计算工作日的部分
    """
    if start >= end:
        return 0.0
    
    total_hours = 0.0
    current = start
    
    # 如果开始时间和结束时间在同一天
    if start.date() == end.date():
        if is_workday(start):
            delta = end - start
            total_hours = delta.total_seconds() / 3600.0
        return total_hours
    
    # 处理第一天（从开始时间到当天结束）
    if is_workday(start):
        end_of_day = datetime.combine(start.date(), datetime.max.time().replace(microsecond=0))
        delta = end_of_day - start
        total_hours += delta.total_seconds() / 3600.0
    
    # 处理中间完整的工作日
    current_date = start.date() + timedelta(days=1)
    end_date = end.date()
    
    while current_date < end_date:
        if is_workday(datetime.combine(current_date, datetime.min.time())):
            total_hours += 24.0  # 完整的一天
        current_date += timedelta(days=1)
    
    # 处理最后一天（从当天开始到结束时间）
    if is_workday(end):
        start_of_day = datetime.combine(end.date(), datetime.min.time())
        delta = end - start_of_day
        total_hours += delta.total_seconds() / 3600.0
    
    return total_hours


def add_workdays(start: datetime, workdays: int) -> datetime:
    """
    在指定日期基础上增加指定数量的工作日
    """
    current = start
    added = 0
    
    while added < workdays:
        current += timedelta(days=1)
        if is_workday(current):
            added += 1
    
    return current

