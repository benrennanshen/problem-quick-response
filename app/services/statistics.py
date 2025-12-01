"""
统计计算服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models import StudentRequest
from app.utils.date_utils import (
    parse_datetime,
    is_workday,
    get_workdays_between,
    get_workday_hours_between,
    add_workdays
)
from app.services.similarity import find_duplicate_requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class StatisticsService:
    """
    统计服务类
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def _format_percentage(value: float) -> str:
        percentage = round(value * 100, 2)
        if percentage.is_integer():
            return f"{int(percentage)}%"
        return f"{percentage}%"

    @staticmethod
    def _format_hours(hours: float) -> str:
        rounded = round(hours, 2)
        if rounded.is_integer():
            return f"{int(rounded)}小时"
        return f"{rounded}小时"

    @staticmethod
    def _format_id_list(id_list: List[str]) -> str:
        return ",".join(id_list) if id_list else ""

    @staticmethod
    def _normalize_category(category: str) -> str:
        if not category:
            return "未分类"
        parts = [p.strip() for p in category.split("/") if p.strip()]
        if len(parts) >= 2:
            return parts[1]
        return parts[0] if parts else "未分类"

    @staticmethod
    def _format_issue_summary(texts: List[str]) -> str:
        cleaned = [text.strip() for text in texts if text and text.strip()]
        return "\n".join(f"{idx}. {text}" for idx, text in enumerate(cleaned, start=1))

    @staticmethod
    def _serialize_request(record: StudentRequest) -> Dict:
        return {
            '诉求ID': record.id,
            '诉求分类': record.category,
            '所属院系': record.department,
            '是否超时': record.is_overdue,
            '受理单位': record.handling_unit,
            '受理时间': record.receive_time,
            '完成时间': record.finish_time,
            '处理时长': record.processing_duration,
            '标题': record.title,
            '学号/教工号': record.student_staff_id,
            '姓名': record.name,
            '手机号': record.phone_number,
            '联系方式': record.contact_method,
            '状态': record.status,
            '满意度': record.satisfaction,
            '提交时间': record.submit_time,
            '内容': record.content,
            '用户回复': record.user_response,
        }
    
    def calculate_statistics(self, start_time: str, end_time: str) -> Dict:
        """
        计算统计数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            统计结果字典
        """
        try:
            # 解析时间
            start_dt = parse_datetime(start_time)
            end_dt = parse_datetime(end_time)
        except Exception as e:
            logger.error(f"时间解析失败: {e}")
            raise ValueError(f"时间格式错误: {e}")
        
        # 查询时间范围内的所有记录
        query = self.db.query(StudentRequest).filter(
            and_(
                StudentRequest.submit_time.isnot(None),
                StudentRequest.submit_time != ''
            )
        )
        
        # 过滤时间范围（需要将字符串时间转换为可比较的格式）
        # 由于时间存储为字符串，我们需要在应用层进行过滤
        all_requests = query.all()
        
        # 转换为字典列表并过滤时间范围
        requests_data = []
        for req in all_requests:
            try:
                submit_dt = parse_datetime(req.submit_time)
                if start_dt <= submit_dt <= end_dt:
                    requests_data.append({
                        'id': req.id,
                        'student_staff_id': req.student_staff_id,
                        'title': req.title or '',
                        'content': req.content or '',
                        'submit_time': req.submit_time,
                        'receive_time': req.receive_time,
                        'finish_time': req.finish_time,
                        'status': req.status or '',
                        'category': req.category or '',
                        'handling_unit': req.handling_unit or '未指定受理单位'
                    })
            except Exception as e:
                logger.warning(f"解析记录 {req.id} 的时间失败: {e}")
                continue
        
        total_count = len(requests_data)
        
        if total_count == 0:
            return self._empty_statistics()
        
        # 计算各项指标
        accepted_count = sum(1 for r in requests_data if r['receive_time'] and r['receive_time'].strip())
        completed_count = sum(1 for r in requests_data if r['finish_time'] and r['finish_time'].strip())
        
        acceptance_rate = accepted_count / total_count if total_count > 0 else 0.0
        completion_rate = completed_count / total_count if total_count > 0 else 0.0
        
        # 计算办结时间相关的指标
        completion_stats = self._calculate_completion_stats(requests_data)
        
        # 计算按受理单位的统计
        department_statistics = self._calculate_department_stats(requests_data)

        # 计算重复提交
        duplicate_submissions, duplicate_submission_ids = find_duplicate_requests(
            requests_data,
            similarity_threshold=0.8
        )
        duplicate_submission_ids_str = ",".join(duplicate_submission_ids)
        
        # 计算超过7天后的办结率
        over_7_days_completion_rate = (
            completion_stats['completed_over_7_days'] / completed_count
            if completed_count > 0 else 0.0
        )

        return {
            'total_count': total_count,
            'accepted_count': accepted_count,
            'acceptance_rate': self._format_percentage(acceptance_rate),
            'completed_count': completed_count,
            'completion_rate': self._format_percentage(completion_rate),
            'completed_in_one_workday': completion_stats['completed_in_one_workday'],
            'completed_in_3_days': completion_stats['completed_in_3_days'],
            'completed_in_7_days': completion_stats['completed_in_7_days'],
            'completed_over_7_days': completion_stats['completed_over_7_days'],
            'over_7_days_completion_rate': self._format_percentage(over_7_days_completion_rate),
            'average_completion_hours': self._format_hours(completion_stats['average_completion_hours']),
            'duplicate_submissions': duplicate_submissions,
            'duplicate_submission_ids': duplicate_submission_ids_str,
            'completed_in_one_workday_ids': self._format_id_list(completion_stats['completed_in_one_workday_ids']),
            'completed_in_3_days_ids': self._format_id_list(completion_stats['completed_in_3_days_ids']),
            'completed_in_7_days_ids': self._format_id_list(completion_stats['completed_in_7_days_ids']),
            'completed_over_7_days_ids': self._format_id_list(completion_stats['completed_over_7_days_ids']),
            'department_statistics': department_statistics,
            'category_statistics': self._calculate_category_stats(requests_data, total_count)
        }
    
    def _calculate_completion_stats(self, requests_data: List[Dict]) -> Dict:
        """
        计算办结时间相关的统计
        
        Returns:
            包含办结时间统计的字典
        """
        completed_requests = [
            r for r in requests_data
            if r['receive_time'] and r['receive_time'].strip() and
               r['finish_time'] and r['finish_time'].strip()
        ]
        
        if not completed_requests:
            return {
                'completed_in_one_workday': 0,
                'completed_in_3_days': 0,
                'completed_in_7_days': 0,
                'completed_over_7_days': 0,
                'average_completion_hours': 0.0
            }
        
        completed_in_one_workday = 0
        completed_in_3_days = 0
        completed_in_7_days = 0
        completed_over_7_days = 0
        within_one_workday_ids: List[str] = []
        within_3_days_ids: List[str] = []
        within_7_days_ids: List[str] = []
        over_7_days_ids: List[str] = []
        total_hours = 0.0
        valid_hours_count = 0
        
        for req in completed_requests:
            try:
                receive_dt = parse_datetime(req['receive_time'])
                finish_dt = parse_datetime(req['finish_time'])
                
                if finish_dt < receive_dt:
                    continue  # 完成时间早于受理时间，数据异常，跳过
                
                # 计算工作日数
                workdays = get_workdays_between(receive_dt, finish_dt)
                
                # 计算工作小时数
                work_hours = get_workday_hours_between(receive_dt, finish_dt)
                
                if work_hours > 0:
                    total_hours += work_hours
                    valid_hours_count += 1
                
                # 统计不同时间段的办结数量（互斥统计）
                record_id = req.get('id')
                if workdays <= 1:
                    completed_in_one_workday += 1
                    if record_id:
                        within_one_workday_ids.append(record_id)
                elif workdays <= 3:
                    completed_in_3_days += 1
                    if record_id:
                        within_3_days_ids.append(record_id)
                elif workdays <= 7:
                    completed_in_7_days += 1
                    if record_id:
                        within_7_days_ids.append(record_id)
                else:
                    completed_over_7_days += 1
                    if record_id:
                        over_7_days_ids.append(record_id)
                    
            except Exception as e:
                logger.warning(f"计算记录 {req.get('id')} 的办结时间失败: {e}")
                continue
        
        average_completion_hours = (
            total_hours / valid_hours_count
            if valid_hours_count > 0 else 0.0
        )
        
        return {
            'completed_in_one_workday': completed_in_one_workday,
            'completed_in_3_days': completed_in_3_days,
            'completed_in_7_days': completed_in_7_days,
            'completed_over_7_days': completed_over_7_days,
            'average_completion_hours': average_completion_hours,
            'completed_in_one_workday_ids': within_one_workday_ids,
            'completed_in_3_days_ids': within_3_days_ids,
            'completed_in_7_days_ids': within_7_days_ids,
            'completed_over_7_days_ids': over_7_days_ids
        }
    
    def _empty_statistics(self) -> Dict:
        """
        返回空统计数据
        """
        return {
            'total_count': 0,
            'accepted_count': 0,
            'acceptance_rate': "0%",
            'completed_count': 0,
            'completion_rate': "0%",
            'completed_in_one_workday': 0,
            'completed_in_3_days': 0,
            'completed_in_7_days': 0,
            'completed_over_7_days': 0,
            'over_7_days_completion_rate': "0%",
            'average_completion_hours': "0小时",
            'duplicate_submissions': 0,
            'duplicate_submission_ids': "",
            'completed_in_one_workday_ids': "",
            'completed_in_3_days_ids': "",
            'completed_in_7_days_ids': "",
            'completed_over_7_days_ids': "",
            'department_statistics': [],
            'category_statistics': []
        }

    def _calculate_department_stats(self, requests_data: List[Dict]) -> List[Dict]:
        """
        按受理单位统计办结情况
        """
        if not requests_data:
            return []

        department_stats: Dict[str, Dict] = {}

        for req in requests_data:
            handling_unit = req.get('handling_unit') or '未指定受理单位'
            stats = department_stats.setdefault(handling_unit, {
                'handling_unit': handling_unit,
                'total_count': 0,
                'accepted_count': 0,
                'completed_count': 0,
                'completed_in_one_workday': 0,
                'completed_in_3_days': 0,
                'completed_in_7_days': 0,
                'completed_over_7_days': 0,
                'requests': []
            })

            stats['total_count'] += 1
            stats['requests'].append({
                'id': req.get('id'),
                'student_staff_id': req.get('student_staff_id'),
                'title': req.get('title', ''),
                'content': req.get('content', '')
            })

            if req.get('receive_time') and req['receive_time'].strip():
                stats['accepted_count'] += 1

            if req.get('finish_time') and req['finish_time'].strip():
                stats['completed_count'] += 1
                try:
                    receive_dt = parse_datetime(req['receive_time'])
                    finish_dt = parse_datetime(req['finish_time'])

                    if finish_dt < receive_dt:
                        continue

                    workdays = get_workdays_between(receive_dt, finish_dt)

                    if workdays <= 1:
                        stats['completed_in_one_workday'] += 1
                    elif workdays <= 3:
                        stats['completed_in_3_days'] += 1
                    elif workdays <= 7:
                        stats['completed_in_7_days'] += 1
                    else:
                        stats['completed_over_7_days'] += 1
                except Exception as e:
                    logger.warning(f"计算受理单位 {handling_unit} 的办结时间失败: {e}")
                    continue

        department_list = []
        for stats in department_stats.values():
            duplicate_submissions, duplicate_ids = find_duplicate_requests(
                stats['requests'],
                similarity_threshold=0.8
            )
            stats['duplicate_submissions'] = duplicate_submissions
            stats['duplicate_submission_ids'] = ",".join(duplicate_ids) if duplicate_ids else ""
            stats.pop('requests', None)
            department_list.append(stats)

        # 转换为列表并按总量降序排序
        return sorted(department_list, key=lambda x: x['total_count'], reverse=True)

    def _calculate_category_stats(self, requests_data: List[Dict], total_count: int) -> List[Dict]:
        """
        诉求分类统计：受理量、占比、问题汇总
        """
        if not requests_data or total_count == 0:
            return []

        category_stats: Dict[str, Dict] = {}
        for req in requests_data:
            category = self._normalize_category(req.get('category', ''))
            stats = category_stats.setdefault(category, {
                'category': category,
                'total_count': 0,
                'issues': []
            })
            stats['total_count'] += 1
            issue_text = req.get('content') or req.get('title') or ''
            if issue_text:
                stats['issues'].append(issue_text)

        result = []
        for data in category_stats.values():
            percentage = data['total_count'] / total_count
            summary = self._format_issue_summary(data['issues'])
            result.append({
                'category': data['category'],
                'total_count': data['total_count'],
                'percentage': self._format_percentage(percentage),
                'issues_summary': summary
            })

        return sorted(result, key=lambda x: x['total_count'], reverse=True)

    def get_requests_by_ids(self, ids: List[str]) -> List[Dict]:
        """
        根据ID列表获取诉求详情
        """
        if not ids:
            return []

        records = (
            self.db.query(StudentRequest)
            .filter(StudentRequest.id.in_(ids))
            .all()
        )
        return [self._serialize_request(record) for record in records]

