"""
测试数据生成器
生成用于测试明细接口和汇总接口的测试数据
"""
import sys
import os
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models import StudentRequest
from app.utils.date_utils import add_workdays


# 测试数据配置
TEST_DATA_COUNT = 150  # 生成的测试数据条数

# 测试数据池
HANDLING_UNITS = [
    '教务处', '学生工作处', '后勤保障处', '图书馆', '信息中心',
    '财务处', '保卫处', '校医院', '体育部', '国际交流处'
]

DEPARTMENTS = [
    '计算机学院', '软件学院', '信息学院', '数学学院', '物理学院',
    '化学学院', '生物学院', '文学院', '外国语学院', '经济管理学院'
]

CATEGORIES = [
    '教学管理/课程安排', '教学管理/成绩查询', '教学管理/选课问题',
    '生活服务/宿舍管理', '生活服务/食堂餐饮', '生活服务/校园网络',
    '行政服务/证件办理', '行政服务/财务报销', '行政服务/档案管理',
    '设施服务/教室设备', '设施服务/图书馆资源', '设施服务/体育场馆'
]

STATUSES = [
    '待受理', '受理中', '已办结', '已关闭'
]

SATISFACTIONS = [
    '非常满意', '满意', '一般', '不满意', '未评价'
]

CONTENTS = [
    '请问这个学期的选课时间是什么时候？',
    '宿舍空调坏了，需要维修。',
    '图书馆闭馆时间能否延长？',
    '食堂饭菜价格有点贵，希望能改善。',
    '校园网经常断连，影响学习。',
    '请问补办学生证需要什么材料？',
    '教室投影仪无法使用，请及时维修。',
    '体育场馆预约系统一直无法登录。',
    '请问实习学分如何认定？',
    '宿舍楼道灯坏了，存在安全隐患。',
    '希望增加更多的自习室开放时间。',
    '请问奖学金评定标准是什么？',
    '校园卡丢失，如何补办？',
    '食堂工作人员服务态度很好，提出表扬。',
    '建议增加校园公交线路。'
]

IS_OVERDUE = ['是', '否', '否', '否', '否']  # 20% 超时率


def generate_random_id() -> str:
    """
    生成随机诉求ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = random.randint(1000, 9999)
    return f"REQ{timestamp}{random_suffix}"


def generate_random_student_info() -> tuple:
    """
    生成随机的学生信息
    """
    student_id = f"{random.randint(2020001, 2024999)}"
    names = ['张伟', '李娜', '王强', '刘洋', '陈静', '杨帆', '赵敏', '黄磊', '周杰', '吴芳']
    name = random.choice(names)
    phone = f"138{random.randint(10000000, 99999999)}"
    return student_id, name, phone


def generate_random_datetime(start_date: datetime, end_date: datetime) -> str:
    """
    生成指定范围内的随机时间
    """
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_seconds = random.randrange(86400)
    random_date = start_date + timedelta(days=random_days, seconds=random_seconds)
    return random_date.strftime("%Y-%m-%d %H:%M:%S")


def calculate_finish_time(receive_time: str, status: str) -> tuple:
    """
    根据受理时间和状态计算完成时间
    返回 (完成时间字符串, 处理时长字符串)
    """
    if status not in ['已办结', '已关闭']:
        return '', ''

    receive_dt = datetime.strptime(receive_time, "%Y-%m-%d %H:%M:%S")

    # 随机生成 1-10 个工作日的办结时间
    workdays = random.randint(1, 10)
    finish_dt = add_workdays(receive_dt, workdays)

    # 计算处理时长
    delta = finish_dt - receive_dt
    hours = delta.total_seconds() / 3600
    processing_duration = f"{hours:.1f}小时"

    return finish_dt.strftime("%Y-%m-%d %H:%M:%S"), processing_duration


def generate_test_record(record_index: int, start_date: datetime, end_date: datetime) -> StudentRequest:
    """
    生成一条测试记录
    """
    # 生成提交时间
    submit_time = generate_random_datetime(start_date, end_date)
    submit_dt = datetime.strptime(submit_time, "%Y-%m-%d %H:%M:%S")

    # 随机选择状态
    status = random.choices(STATUSES, weights=[0.1, 0.15, 0.65, 0.1])[0]

    # 生成受理时间（90% 的记录有受理时间）
    if random.random() < 0.9:
        receive_hours = random.randint(1, 48)
        receive_dt = submit_dt + timedelta(hours=receive_hours)
        receive_time = receive_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        receive_time = ''

    # 生成完成时间和处理时长
    if receive_time:
        finish_time, processing_duration = calculate_finish_time(receive_time, status)
    else:
        finish_time = ''
        processing_duration = ''

    # 生成学生信息
    student_id, name, phone = generate_random_student_info()

    # 创建记录
    record = StudentRequest(
        id=generate_random_id(),
        category=random.choice(CATEGORIES),
        department=random.choice(DEPARTMENTS),
        is_overdue=random.choice(IS_OVERDUE),
        handling_unit=random.choice(HANDLING_UNITS),
        receive_time=receive_time,
        finish_time=finish_time,
        processing_duration=processing_duration,
        title=f"诉求{record_index + 1}：" + random.choice(CONTENTS)[:50],
        student_staff_id=student_id,
        name=name,
        phone_number=phone,
        contact_method=f"手机: {phone}",
        status=status,
        satisfaction=random.choice(SATISFACTIONS) if status in ['已办结', '已关闭'] else '',
        submit_time=submit_time,
        content=random.choice(CONTENTS),
        user_response=''  # 初始无回复
    )

    return record


def clear_existing_data(db: Session):
    """
    清除现有的测试数据
    """
    print("正在清除现有数据...")
    try:
        # 尝试使用 ORM 删除
        db.query(StudentRequest).delete()
        db.commit()
        print("数据清除完成。")
    except Exception as e:
        # 如果表不可更新（可能是视图），则跳过
        print(f"注意: 无法清除数据 (表可能是视图): {e}")
        print("将直接插入新数据...")
        db.rollback()


def generate_test_data(count: int = TEST_DATA_COUNT):
    """
    生成测试数据
    """
    print(f"开始生成 {count} 条测试数据...")

    # 创建数据库会话
    db = SessionLocal()

    try:
        # 确保表存在
        Base.metadata.create_all(bind=engine)

        # 询问是否清除现有数据
        existing_count = db.query(StudentRequest).count()
        if existing_count > 0:
            print(f"数据库中已有 {existing_count} 条记录")
            # 在非交互模式下，不清除现有数据，直接追加
            print("将在现有数据基础上追加新记录...")

        # 设置时间范围（最近 60 天）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)

        print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")

        # 生成测试数据
        records = []
        for i in range(count):
            record = generate_test_record(i, start_date, end_date)
            records.append(record)

            # 每 50 条提交一次
            if (i + 1) % 50 == 0:
                try:
                    db.bulk_save_objects(records)
                    db.commit()
                    print(f"已生成 {i + 1} 条记录...")
                except Exception as e:
                    print(f"ORM 插入失败，尝试使用原生 SQL: {e}")
                    db.rollback()
                    # 使用原生 SQL 插入
                    for rec in records:
                        insert_sql = text("""
                            INSERT INTO student_requests (
                                id, category, department, is_overdue, handling_unit,
                                receive_time, finish_time, processing_duration, title,
                                student_staff_id, name, phone_number, contact_method,
                                status, satisfaction, submit_time, content, user_response
                            ) VALUES (
                                :id, :category, :department, :is_overdue, :handling_unit,
                                :receive_time, :finish_time, :processing_duration, :title,
                                :student_staff_id, :name, :phone_number, :contact_method,
                                :status, :satisfaction, :submit_time, :content, :user_response
                            )
                        """)
                        db.execute(insert_sql, {
                            'id': rec.id,
                            'category': rec.category,
                            'department': rec.department,
                            'is_overdue': rec.is_overdue,
                            'handling_unit': rec.handling_unit,
                            'receive_time': rec.receive_time,
                            'finish_time': rec.finish_time,
                            'processing_duration': rec.processing_duration,
                            'title': rec.title,
                            'student_staff_id': rec.student_staff_id,
                            'name': rec.name,
                            'phone_number': rec.phone_number,
                            'contact_method': rec.contact_method,
                            'status': rec.status,
                            'satisfaction': rec.satisfaction,
                            'submit_time': rec.submit_time,
                            'content': rec.content,
                            'user_response': rec.user_response
                        })
                    db.commit()
                records = []

        # 提交剩余记录
        if records:
            try:
                db.bulk_save_objects(records)
                db.commit()
            except Exception as e:
                print(f"ORM 插入失败，尝试使用原生 SQL: {e}")
                db.rollback()
                for rec in records:
                    insert_sql = text("""
                        INSERT INTO student_requests (
                            id, category, department, is_overdue, handling_unit,
                            receive_time, finish_time, processing_duration, title,
                            student_staff_id, name, phone_number, contact_method,
                            status, satisfaction, submit_time, content, user_response
                        ) VALUES (
                            :id, :category, :department, :is_overdue, :handling_unit,
                            :receive_time, :finish_time, :processing_duration, :title,
                            :student_staff_id, :name, :phone_number, :contact_method,
                            :status, :satisfaction, :submit_time, :content, :user_response
                        )
                    """)
                    db.execute(insert_sql, {
                        'id': rec.id,
                        'category': rec.category,
                        'department': rec.department,
                        'is_overdue': rec.is_overdue,
                        'handling_unit': rec.handling_unit,
                        'receive_time': rec.receive_time,
                        'finish_time': rec.finish_time,
                        'processing_duration': rec.processing_duration,
                        'title': rec.title,
                        'student_staff_id': rec.student_staff_id,
                        'name': rec.name,
                        'phone_number': rec.phone_number,
                        'contact_method': rec.contact_method,
                        'status': rec.status,
                        'satisfaction': rec.satisfaction,
                        'submit_time': rec.submit_time,
                        'content': rec.content,
                        'user_response': rec.user_response
                    })
                db.commit()

        print(f"\n测试数据生成完成！共生成 {count} 条记录。")

        # 打印统计信息
        total = db.query(StudentRequest).count()
        accepted = db.query(StudentRequest).filter(
            StudentRequest.receive_time.isnot(None),
            StudentRequest.receive_time != ''
        ).count()
        completed = db.query(StudentRequest).filter(
            StudentRequest.finish_time.isnot(None),
            StudentRequest.finish_time != ''
        ).count()

        print(f"\n数据统计:")
        print(f"  总记录数: {total}")
        print(f"  受理量: {accepted}")
        print(f"  办结量: {completed}")
        print(f"  受理率: {accepted / total * 100:.2f}%" if total > 0 else "  受理率: 0%")
        print(f"  办结率: {completed / total * 100:.2f}%" if total > 0 else "  办结率: 0%")

    except Exception as e:
        print(f"生成测试数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='生成测试数据')
    parser.add_argument(
        '--count',
        type=int,
        default=TEST_DATA_COUNT,
        help=f'生成的记录数量（默认: {TEST_DATA_COUNT}）'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='清除现有数据后再生成'
    )

    args = parser.parse_args()

    # 如果指定了 --clear，直接清除
    if args.clear:
        db = SessionLocal()
        try:
            clear_existing_data(db)
        finally:
            db.close()

    generate_test_data(args.count)
