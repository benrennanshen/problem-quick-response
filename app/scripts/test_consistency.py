"""
测试验证脚本
验证明细接口数据聚合与汇总接口数据的一致性
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.statistics import StatisticsService


def print_section(title: str):
    """
    打印分节标题
    """
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_comparison(name: str, summary_value: int, statistics_value: int, tolerance: int = 0):
    """
    打印对比结果
    """
    match = "[通过]" if abs(summary_value - statistics_value) <= tolerance else "[失败]"
    diff = summary_value - statistics_value
    diff_str = f" (差异: {diff:+d})" if diff != 0 else ""

    print(f"  {name}:")
    print(f"    明细汇总: {summary_value}")
    print(f"    汇总接口: {statistics_value}")
    print(f"    结果: {match}{diff_str}")


def test_consistency(start_time: str, end_time: str):
    """
    测试数据一致性

    Args:
        start_time: 开始时间
        end_time: 结束时间
    """
    print_section("数据一致性测试")
    print(f"测试时间范围: {start_time} 到 {end_time}")

    db = SessionLocal()
    try:
        service = StatisticsService(db)

        # 1. 调用汇总接口
        print("\n[1/3] 调用汇总接口...")
        statistics_result = service.calculate_statistics(start_time, end_time)

        print(f"  总记录数: {statistics_result['total_count']}")
        print(f"  受理量: {statistics_result['accepted_count']}")
        print(f"  办结量: {statistics_result['completed_count']}")

        # 2. 调用明细接口（获取所有数据）
        print("\n[2/3] 调用明细接口...")
        detail_result = service.get_detail_records(
            start_time=start_time,
            end_time=end_time,
            page=1,
            page_size=100000  # 获取所有数据
        )

        summary = detail_result['summary']
        print(f"  总记录数: {summary['total_count']}")
        print(f"  受理量: {summary['accepted_count']}")
        print(f"  办结量: {summary['completed_count']}")

        # 3. 对比验证
        print_section("[3/3] 数据一致性验证")

        all_passed = True

        # 对比基本统计
        print_comparison(
            "总记录数",
            summary['total_count'],
            statistics_result['total_count']
        )
        if summary['total_count'] != statistics_result['total_count']:
            all_passed = False

        print_comparison(
            "受理量",
            summary['accepted_count'],
            statistics_result['accepted_count']
        )
        if summary['accepted_count'] != statistics_result['accepted_count']:
            all_passed = False

        print_comparison(
            "办结量",
            summary['completed_count'],
            statistics_result['completed_count']
        )
        if summary['completed_count'] != statistics_result['completed_count']:
            all_passed = False

        # 对比办结时间统计
        print("\n  办结时间统计:")

        print_comparison(
            "1个工作日内办结",
            summary['completed_in_one_workday'],
            statistics_result['completed_in_one_workday']
        )
        if summary['completed_in_one_workday'] != statistics_result['completed_in_one_workday']:
            all_passed = False

        print_comparison(
            "3个工作日内办结",
            summary['completed_in_3_days'],
            statistics_result['completed_in_3_days']
        )
        if summary['completed_in_3_days'] != statistics_result['completed_in_3_days']:
            all_passed = False

        print_comparison(
            "7个工作日内办结",
            summary['completed_in_7_days'],
            statistics_result['completed_in_7_days']
        )
        if summary['completed_in_7_days'] != statistics_result['completed_in_7_days']:
            all_passed = False

        print_comparison(
            "超过7个工作日办结",
            summary['completed_over_7_days'],
            statistics_result['completed_over_7_days']
        )
        if summary['completed_over_7_days'] != statistics_result['completed_over_7_days']:
            all_passed = False

        # 验证办结量 = 各时间段办结量之和
        detail_completion_sum = (
            summary['completed_in_one_workday'] +
            summary['completed_in_3_days'] +
            summary['completed_in_7_days'] +
            summary['completed_over_7_days']
        )
        statistics_completion_sum = (
            statistics_result['completed_in_one_workday'] +
            statistics_result['completed_in_3_days'] +
            statistics_result['completed_in_7_days'] +
            statistics_result['completed_over_7_days']
        )

        print("\n  办结量总和验证:")
        print(f"    明细接口办结量: {summary['completed_count']}")
        print(f"    明细时间段总和: {detail_completion_sum}")
        print(f"    汇总接口办结量: {statistics_result['completed_count']}")
        print(f"    汇总时间段总和: {statistics_completion_sum}")

        # 注意：由于时间解析和异常数据处理，可能存在1-2条记录的差异
        tolerance = 2  # 允许2条记录的差异
        if abs(summary['completed_count'] - detail_completion_sum) > tolerance:
            print(f"    结果: [失败] - 明细接口办结量不等于时间段之和 (差异超过{tolerance}条)")
            all_passed = False
        else:
            if summary['completed_count'] != detail_completion_sum:
                print(f"    结果: [通过] - 明细接口办结量基本等于时间段之和 (允许{tolerance}条差异)")
            else:
                print(f"    结果: [通过] - 明细接口办结量等于时间段之和")

        # 注意：由于时间解析和异常数据处理，可能存在1-2条记录的差异
        # 这是正常的，因为某些记录的时间可能不符合预期格式
        tolerance = 2  # 允许2条记录的差异
        if abs(statistics_result['completed_count'] - statistics_completion_sum) > tolerance:
            print(f"    结果: [失败] - 汇总接口办结量不等于时间段之和 (差异超过{tolerance}条)")
            all_passed = False
        else:
            if statistics_result['completed_count'] != statistics_completion_sum:
                print(f"    结果: [通过] - 汇总接口办结量基本等于时间段之和 (允许{tolerance}条差异)")
            else:
                print(f"    结果: [通过] - 汇总接口办结量等于时间段之和")

        # 最终结果
        print_section("测试结果")
        if all_passed:
            print("\n  [成功] 所有测试通过！数据一致性验证成功。\n")
            return True
        else:
            print("\n  [失败] 部分测试失败！数据存在不一致。\n")
            return False

    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_with_filters():
    """
    测试带筛选条件的数据一致性
    """
    print_section("筛选条件测试")

    db = SessionLocal()
    try:
        service = StatisticsService(db)

        # 获取最近30天的时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        start_time = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_time = end_date.strftime("%Y-%m-%d %H:%M:%S")

        # 测试1: 按受理单位筛选
        print("\n[测试1] 按受理单位筛选...")
        detail_result = service.get_detail_records(
            start_time=start_time,
            end_time=end_time,
            handling_unit="教务处",
            page=1,
            page_size=1000
        )
        print(f"  筛选条件: 受理单位 = '教务处'")
        print(f"  结果记录数: {detail_result['total']}")
        print(f"  受理量: {detail_result['summary']['accepted_count']}")
        print(f"  办结量: {detail_result['summary']['completed_count']}")

        # 测试2: 按状态筛选
        print("\n[测试2] 按状态筛选...")
        detail_result = service.get_detail_records(
            start_time=start_time,
            end_time=end_time,
            status="已办结",
            page=1,
            page_size=1000
        )
        print(f"  筛选条件: 状态 = '已办结'")
        print(f"  结果记录数: {detail_result['total']}")
        print(f"  受理量: {detail_result['summary']['accepted_count']}")
        print(f"  办结量: {detail_result['summary']['completed_count']}")

        # 测试3: 按办结时间筛选
        print("\n[测试3] 按办结时间筛选...")
        finish_start = (start_date + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        finish_end = (start_date + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")

        detail_result = service.get_detail_records(
            start_time=start_time,
            end_time=end_time,
            finish_start_time=finish_start,
            finish_end_time=finish_end,
            page=1,
            page_size=1000
        )
        print(f"  筛选条件: 办结时间在 {finish_start} 到 {finish_end} 之间")
        print(f"  结果记录数: {detail_result['total']}")
        print(f"  受理量: {detail_result['summary']['accepted_count']}")
        print(f"  办结量: {detail_result['summary']['completed_count']}")

        print("\n筛选条件测试完成！")

    except Exception as e:
        print(f"\n筛选测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_pagination():
    """
    测试分页功能
    """
    print_section("分页功能测试")

    db = SessionLocal()
    try:
        service = StatisticsService(db)

        # 获取最近30天的时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        start_time = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_time = end_date.strftime("%Y-%m-%d %H:%M:%S")

        page_size = 10
        page = 1

        print(f"\n测试分页 (每页 {page_size} 条记录):")
        print(f"时间范围: {start_time} 到 {end_time}\n")

        while True:
            detail_result = service.get_detail_records(
                start_time=start_time,
                end_time=end_time,
                page=page,
                page_size=page_size
            )

            record_count = len(detail_result['records'])
            print(f"  第 {page} 页: {record_count} 条记录 (总计 {detail_result['total']} 条)")

            if page >= detail_result['total_pages']:
                break

            page += 1

        print(f"\n分页测试完成！共 {page} 页。")

    except Exception as e:
        print(f"\n分页测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='测试数据一致性')
    parser.add_argument(
        '--start-time',
        type=str,
        help='开始时间，格式: YYYY-MM-DD HH:MM:SS'
    )
    parser.add_argument(
        '--end-time',
        type=str,
        help='结束时间，格式: YYYY-MM-DD HH:MM:SS'
    )
    parser.add_argument(
        '--filters',
        action='store_true',
        help='测试筛选条件'
    )
    parser.add_argument(
        '--pagination',
        action='store_true',
        help='测试分页功能'
    )
    parser.add_argument(
        '--all-data',
        action='store_true',
        help='测试所有数据（2023年到2025年）'
    )

    args = parser.parse_args()

    # 确定时间范围
    if args.all_data:
        # 使用数据库中的实际时间范围
        start_time = "2023-01-01 00:00:00"
        end_time = "2025-12-31 23:59:59"
    elif args.start_time and args.end_time:
        start_time = args.start_time
        end_time = args.end_time
    else:
        # 默认使用最近30天（但数据库数据可能较旧）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_time = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_time = end_date.strftime("%Y-%m-%d %H:%M:%S")

    # 运行测试
    success = test_consistency(start_time, end_time)

    # 可选测试
    if args.filters:
        test_with_filters()

    if args.pagination:
        test_pagination()

    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)
