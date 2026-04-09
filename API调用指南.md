# 接诉即办统计系统 API 调用完整指南

## 基本信息

- **服务名称**: 接诉即办统计系统
- **Base URL**: `http://192.168.1.10:8004/problem-quick-response`
- **请求方式**: POST
- **Content-Type**: application/json

## 时间格式规则

- **推荐**: 只传日期，如 `"2024-01-01"`
- **可选**: 传完整时间，如 `"2024-01-01 08:30:00"`
- 接口会自动补全：开始时间补 `00:00:00`，结束时间补 `23:59:59`

---

## 接口 1：统计数据

**路径**: `POST /api/statistics`

### 请求参数
```json
{
  "start_time": "2024-01-01",
  "end_time": "2024-12-31"
}
```

### 返回字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| httCode | int | HTTP状态码，200表示成功 |
| message | str | 提示信息 |
| data.total_count | int | 数据总量（提交的诉求总数） |
| data.accepted_count | int | 受理量（已被受理的数量） |
| data.acceptance_rate | str | 受理率（百分比，如"95.5%"） |
| data.completed_count | int | 办结量（已完成的数量） |
| data.completion_rate | str | 办结率（百分比） |
| data.completed_in_one_workday | int | 1个工作日内办结数量 |
| data.completed_in_one_workday_ids | str | 1个工作日办结的记录ID，逗号分隔 |
| data.completed_in_3_days | int | 3个工作日内办结数量 |
| data.completed_in_3_days_ids | str | 3天内办结的记录ID，逗号分隔 |
| data.completed_in_7_days | int | 7个工作日内办结数量 |
| data.completed_in_7_days_ids | str | 7天内办结的记录ID，逗号分隔 |
| data.completed_over_7_days | int | 超过7个工作日办结数量 |
| data.completed_over_7_days_ids | str | 超过7天办结的记录ID，逗号分隔 |
| data.over_7_days_completion_rate | str | 超过7天后的办结率 |
| data.average_completion_hours | str | 平均办结时间（如"48.5小时"） |
| data.duplicate_submissions | int | 重复提交数量 |
| data.duplicate_submission_ids | str | 重复提交的记录ID，逗号分隔 |
| data.department_statistics | array | 按受理单位汇总的统计 |
| data.category_statistics | array | 诉求分类统计 |

### 部门统计 (department_statistics)
| 字段 | 说明 |
|------|------|
| handling_unit | 受理单位名称 |
| total_count | 该部门总件数 |
| accepted_count | 该部门受理量 |
| completed_count | 该部门办结量 |
| completed_in_one_workday | 该部门1个工作日内办结数 |
| completed_in_3_days | 该部门3个工作日内办结数 |
| completed_in_7_days | 该部门7个工作日内办结数 |
| completed_over_7_days | 该部门超过7天办结数 |
| duplicate_submissions | 该部门重复提交数 |
| duplicate_submission_ids | 该部门重复提交的记录ID |

### 分类统计 (category_statistics)
| 字段 | 说明 |
|------|------|
| category | 诉求分类 |
| total_count | 该分类受理量 |
| percentage | 占比（百分比） |
| issues_summary | 问题汇总（编号+内容） |

### 返回示例
```json
{
  "httCode": 200,
  "message": "success",
  "data": {
    "total_count": 1000,
    "accepted_count": 950,
    "acceptance_rate": "95%",
    "completed_count": 900,
    "completion_rate": "90%",
    "completed_in_one_workday": 200,
    "completed_in_one_workday_ids": "id1,id2,id3",
    "completed_in_3_days": 400,
    "completed_in_3_days_ids": "id4,id5,id6",
    "completed_in_7_days": 600,
    "completed_in_7_days_ids": "id7,id8,id9",
    "completed_over_7_days": 300,
    "completed_over_7_days_ids": "id10,id11,id12",
    "over_7_days_completion_rate": "30%",
    "average_completion_hours": "48.5小时",
    "duplicate_submissions": 50,
    "duplicate_submission_ids": "id1,id2,id3",
    "department_statistics": [
      {
        "handling_unit": "信息中心",
        "total_count": 200,
        "accepted_count": 190,
        "completed_count": 180,
        "completed_in_one_workday": 50,
        "completed_in_3_days": 80,
        "completed_in_7_days": 120,
        "completed_over_7_days": 60,
        "duplicate_submissions": 10,
        "duplicate_submission_ids": "id1,id2,id3"
      },
      {
        "handling_unit": "后勤处",
        "total_count": 150,
        "accepted_count": 145,
        "completed_count": 140,
        "completed_in_one_workday": 40,
        "completed_in_3_days": 60,
        "completed_in_7_days": 90,
        "completed_over_7_days": 50,
        "duplicate_submissions": 5,
        "duplicate_submission_ids": "id4,id5"
      }
    ],
    "category_statistics": [
      {
        "category": "网络问题",
        "total_count": 300,
        "percentage": "30%",
        "issues_summary": "1. 宿舍网络无法连接\n2. WiFi信号弱\n3. 网速慢"
      },
      {
        "category": "生活服务",
        "total_count": 250,
        "percentage": "25%",
        "issues_summary": "1. 食堂饭菜问题\n2. 宿舍空调损坏\n3. 停水问题"
      },
      {
        "category": "教学设施",
        "total_count": 200,
        "percentage": "20%",
        "issues_summary": "1. 教室投影仪故障\n2. 多媒体设备问题"
      }
    ]
  }
}
```

---

## 接口 2：明细查询

**路径**: `POST /api/statistics/detail`

### 请求参数
```json
{
  "start_time": "2024-01-01",
  "end_time": "2024-12-31",
  "handling_unit": "信息中心",
  "category": "网络问题",
  "status": "已完成",
  "finish_start_time": "2024-01-01",
  "finish_end_time": "2024-12-31",
  "page": 1,
  "page_size": 20
}
```

### 筛选参数说明
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_time | str | 是 | 提交开始时间 |
| end_time | str | 是 | 提交结束时间 |
| handling_unit | str | 否 | 受理单位筛选 |
| category | str | 否 | 诉求分类筛选 |
| status | str | 否 | 状态筛选（如"已完成"） |
| finish_start_time | str | 否 | 办结开始时间 |
| finish_end_time | str | 否 | 办结结束时间 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20，最大100 |

### 返回字段说明

| 字段 | 说明 |
|------|------|
| total | 总记录数 |
| page | 当前页码 |
| page_size | 每页数量 |
| total_pages | 总页数 |
| records | 明细记录数组 |
| summary | 汇总统计对象 |

### 记录字段 (records 数组中每条记录)
| 字段 | 说明 |
|------|------|
| 诉求ID | 唯一标识 |
| 诉求分类 | 诉求类别 |
| 所属院系 | 所属院系 |
| 是否超时 | 是否超时 |
| 受理单位 | 受理单位名称 |
| 受理时间 | 受理时间 |
| 完成时间 | 完成时间 |
| 处理时长 | 处理时长 |
| 标题 | 诉求标题 |
| 学号/教工号 | 学号或教工号 |
| 姓名 | 提交人姓名 |
| 手机号 | 手机号 |
| 联系方式 | 联系方式 |
| 状态 | 当前状态 |
| 满意度 | 满意度评价 |
| 提交时间 | 提交时间 |
| 内容 | 诉求详细内容 |
| 用户回复 | 用户回复内容 |

### 汇总统计 (summary)
| 字段 | 说明 |
|------|------|
| total_count | 总记录数 |
| accepted_count | 受理量 |
| completed_count | 办结量 |
| completed_in_one_workday | 1个工作日内办结数 |
| completed_in_3_days | 3个工作日内办结数 |
| completed_in_7_days | 7个工作日内办结数 |
| completed_over_7_days | 超过7个工作日办结数 |

### 返回示例
```json
{
  "httCode": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "records": [
      {
        "诉求ID": "12345",
        "诉求分类": "网络问题",
        "所属院系": "信息学院",
        "是否超时": "否",
        "受理单位": "信息中心",
        "受理时间": "2024-01-01 10:00:00",
        "完成时间": "2024-01-01 15:00:00",
        "处理时长": "5小时",
        "标题": "宿舍网络无法连接",
        "学号/教工号": "2021001",
        "姓名": "张三",
        "手机号": "13800138000",
        "联系方式": "微信",
        "状态": "已完成",
        "满意度": "满意",
        "提交时间": "2024-01-01 09:00:00",
        "内容": "宿舍网络从昨天开始无法连接，已经尝试重启路由器和电脑，问题依然存在。",
        "用户回复": ""
      },
      {
        "诉求ID": "12346",
        "诉求分类": "生活服务",
        "所属院系": "文学院",
        "是否超时": "否",
        "受理单位": "后勤处",
        "受理时间": "2024-01-02 09:00:00",
        "完成时间": "2024-01-02 16:00:00",
        "处理时长": "7小时",
        "标题": "宿舍空调损坏",
        "学号/教工号": "2021002",
        "姓名": "李四",
        "手机号": "13900139000",
        "联系方式": "电话",
        "状态": "已完成",
        "满意度": "非常满意",
        "提交时间": "2024-01-02 08:00:00",
        "内容": "宿舍空调不制冷，显示E1错误代码，已报修但未处理。",
        "用户回复": "维修师傅已经上门修好了，感谢！"
      },
      {
        "诉求ID": "12347",
        "诉求分类": "教学设施",
        "所属院系": "理学院",
        "是否超时": "是",
        "受理单位": "教务处",
        "受理时间": "2024-01-03 14:00:00",
        "完成时间": null,
        "处理时长": null,
        "标题": "教室投影仪故障",
        "学号/教工号": "2021003",
        "姓名": "王五",
        "手机号": "13700137000",
        "联系方式": "邮件",
        "状态": "处理中",
        "满意度": null,
        "提交时间": "2024-01-03 13:00:00",
        "内容": "A栋302教室投影仪无法开机，影响正常上课使用。",
        "用户回复": null
      }
    ],
    "summary": {
      "total_count": 100,
      "accepted_count": 95,
      "completed_count": 90,
      "completed_in_one_workday": 20,
      "completed_in_3_days": 40,
      "completed_in_7_days": 60,
      "completed_over_7_days": 30
    }
  }
}
```

---

## 接口 3：导出 Excel

**路径**: `POST /api/statistics/detail/export`

### 请求参数
与明细查询相同，但不需要 `page` 和 `page_size`

```json
{
  "start_time": "2024-01-01",
  "end_time": "2024-12-31",
  "handling_unit": "信息中心",
  "category": "网络问题",
  "status": "已完成"
}
```

### 返回
Excel 文件流（可直接下载），包含两个工作表：
1. **明细数据**: 所有符合条件的记录
2. **数据汇总**: 各项统计指标

---

## Python 调用示例

```python
import requests

base_url = "http://192.168.1.10:8004/problem-quick-response"

# 1. 统计数据
response = requests.post(f"{base_url}/api/statistics", json={
    "start_time": "2024-01-01",
    "end_time": "2024-12-31"
})
result = response.json()
print(f"总量: {result['data']['total_count']}")
print(f"受理率: {result['data']['acceptance_rate']}")

# 2. 明细查询
response = requests.post(f"{base_url}/api/statistics/detail", json={
    "start_time": "2024-01-01",
    "end_time": "2024-12-31",
    "page": 1,
    "page_size": 50
})
result = response.json()
for record in result['data']['records']:
    print(f"{record['标题']} - {record['状态']}")

# 3. 导出 Excel
response = requests.post(f"{base_url}/api/statistics/detail/export", json={
    "start_time": "2024-01-01",
    "end_time": "2024-12-31"
})
with open("诉求明细.xlsx", "wb") as f:
    f.write(response.content)
```

---

## 常见查询场景

### 查询今天的数据
```json
{
  "start_time": "2024-01-15",
  "end_time": "2024-01-15"
}
```

### 查询本月的数据
```json
{
  "start_time": "2024-01-01",
  "end_time": "2024-01-31"
}
```

### 查询本年的数据
```json
{
  "start_time": "2024-01-01",
  "end_time": "2024-12-31"
}
```

### 按受理单位筛选
```json
{
  "start_time": "2024-01-01",
  "end_time": "2024-12-31",
  "handling_unit": "信息中心"
}
```

### 按状态筛选
```json
{
  "start_time": "2024-01-01",
  "end_time": "2024-12-31",
  "status": "已完成"
}
```

---

## 错误响应说明

### 请求参数验证失败 (422)
```json
{
  "httCode": 422,
  "message": "请求参数验证失败",
  "data": [
    {
      "loc": ["body", "start_time"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 时间格式错误 (400)
```json
{
  "httCode": 400,
  "message": "时间格式错误: 无法解析日期格式: 2024/13/01",
  "data": null
}
```

### 服务器内部错误 (500)
```json
{
  "httCode": 500,
  "message": "服务器内部错误: 数据库连接失败",
  "data": null
}
```

---

## 常见状态值

### 诉求状态 (status)
- `处理中` - 正在处理中
- `已完成` - 已办结
- `已受理` - 已受理但未完成
- `待受理` - 尚未受理

### 满意度 (satisfaction)
- `非常满意`
- `满意`
- `一般`
- `不满意`
- `非常不满意`

### 是否超时 (is_overdue)
- `是` - 超时
- `否` - 未超时
- `null` - 无法判断（如尚未完成）

---

## 注意事项

1. **时间范围**: `start_time` 必须早于或等于 `end_time`
2. **分页查询**:
   - `page` 从 1 开始，不是 0
   - `page_size` 最大 100，超过会自动限制
3. **筛选条件**:
   - `handling_unit`、`category`、`status` 是精确匹配，不支持模糊查询
   - 多个筛选条件是 **AND** 关系（同时满足）
4. **空值处理**:
   - 未完成的记录，`完成时间`、`处理时长`、`满意度` 可能为 `null`
5. **ID 字段**:
   - `xxx_ids` 字段是逗号分隔的字符串，如 `"id1,id2,id3"`
   - 空列表会返回空字符串 `""`

