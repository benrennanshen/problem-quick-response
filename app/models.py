"""
数据库模型定义
"""
from sqlalchemy import Column, String
from app.database import Base


class StudentRequest(Base):
    """
    学生诉求表模型
    """
    __tablename__ = "student_requests"

    id = Column(String(64), primary_key=True, comment="唯一标识符")
    category = Column(String(64), comment="分类")
    department = Column(String(64), comment="所属院系")
    is_overdue = Column(String(64), comment="是否超时")
    handling_unit = Column(String(64), comment="受理单位")
    receive_time = Column(String(64), comment="受理时间")
    finish_time = Column(String(64), comment="完成时间")
    processing_duration = Column(String(64), comment="处理时长")
    title = Column(String(2000), comment="标题")
    student_staff_id = Column(String(64), comment="学号/教工号")
    name = Column(String(64), comment="姓名")
    phone_number = Column(String(64), comment="手机号")
    contact_method = Column(String(64), comment="联系方式")
    status = Column(String(64), comment="状态")
    satisfaction = Column(String(64), comment="满意度")
    submit_time = Column(String(64), comment="提交时间")
    content = Column(String(2000), comment="内容")
    user_response = Column(String(2000), comment="用户回复")

