"""
日期工具类：处理工作日计算，过滤节假日和周末
"""
import chinese_calendar 
from datetime import datetime, timedelta
from typing import List, Tuple


def parse_datetime(date_str: str) -> datetime:
    """
    解析日期字符串，支持多种格式
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

