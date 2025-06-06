import requests
from typing import Dict, List, Optional

# API配置
BASE_URL = "https://devops-api.nullmax.net/system/api/v1/employee/list"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTExNjI2NjIsImlhdCI6MTc0ODUxMDY2MiwiaXNzIjoi5ZSQ5L-K5ZacIiwicm9sZV9pZCI6IlI1NzIwMzc3NzcyMjE4NzgwOCIsInN1YiI6ImxvZ2luIiwidXNlcl9pZCI6IjQyNiIsIndhcmVob3VzZV9pZHMiOnsiVzU3MjAzNzcwMzA5NzM4NDk2IjoiVzU3MjAzNzcwMzA5NzM4NDk2In19.MJuVPpnrYaGFygsiaE--peOwNmjEUC16plr4d0TN2qY"

# 请求头
headers = {
    "authority": "devops-api.nullmax.net",
    "accept": "application/json, text/plain, */*",
    "authorization": AUTH_TOKEN,
    "origin": "https://devops.nullmax.net",
    "referer": "https://devops.nullmax.net/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
}

def get_employee_list(page: int = -1, page_size: int = 10, is_employed: int = 1) -> Optional[Dict]:
    """
    获取员工列表
    :param page: 页码(-1表示获取所有)
    :param page_size: 每页数量
    :param is_employed: 是否在职(1-在职)
    :return: 包含员工数据的字典或None(出错时)
    """
    params = {
        "page": page,
        "pageSize": page_size,
        "isEmployed": is_employed
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        
        result = response.json()
        
        # 验证返回数据结构
        if not all(key in result for key in ['code', 'msg', 'data']):
            raise ValueError("返回数据缺少必要字段")
            
        if result['code'] != 0:
            raise ValueError(f"API返回错误: {result['msg']} (code: {result['code']})")
            
        if not isinstance(result['data'], dict):
            raise ValueError("data字段不是字典类型")
            
        return result['data']
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 请求错误: {e}")
        return None
    except ValueError as e:
        print(f"🔴 数据解析错误: {e}")
        # if 'response' in locals():
        #     print(f"原始响应: {response.text}")
        return None

def display_employee_data(data: Dict) -> None:
    """格式化显示员工数据"""
    if not data:
        print("没有可显示的数据")
        return
    
    print(f"\n📊 员工数据统计")
    print(f"• 页码: {data.get('page', 'N/A')}")
    print(f"• 每页数量: {data.get('pageSize', 'N/A')}")
    print(f"• 总数: {data.get('total', 0)} 人")
    print(f"• 当前页: {len(data.get('list', []))} 人")
    print("=" * 60)
    
    for idx, employee in enumerate(data.get('list', []), 1):
        print(f"👤 员工 #{idx}")
        print(f"   ID: {employee.get('id', 'N/A')}")
        print(f"   姓名: {employee.get('employeeName', '未知')}")
        # print(f"   邮箱: {employee.get('email', '未提供')}")
        # print(f"   电话: {employee.get('phoneNumber', '未提供')}")
        
        # # 打印其他可能存在的字段
        # extra_fields = {k: v for k, v in employee.items() 
        #                if k not in ['id', 'employeeName', 'email', 'phoneNumber']}
        # if extra_fields:
        #     print("   其他信息:")
        #     for field, value in extra_fields.items():
        #         print(f"     {field}: {value}")
        
        print("-" * 60)

def save_to_json(data: Dict, filename: str = "employee_data.json") -> None:
    """将数据保存为JSON文件"""
    import json
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存为 {filename}")
    except Exception as e:
        print(f"🔴 保存文件失败: {e}")

# if __name__ == "__main__":
#     print("🔄 正在获取员工数据...")
#     employee_data = get_employee_list()
    
#     if employee_data:
#         display_employee_data(employee_data)
        
#         # 询问是否保存数据
#         save_option = input("是否保存数据到JSON文件? (y/n): ").lower()
#         if save_option == 'y':
#             save_to_json(employee_data)
#     else:
#         print("❌ 未能获取员工数据")



import json

def extract_employee_info(file_path):
    """
    从JSON文件中提取list中每个元素的id和employeeName
    
    :param file_path: JSON文件路径
    :return: 包含(id, employeeName)元组的列表
    """
    try:
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证数据结构
        if not all(key in data for key in ['code', 'msg', 'data']):
            raise ValueError("JSON格式不符合预期，缺少必要字段")
        
        if data['code'] != 0:
            print(f"警告: API返回非成功状态 - {data['msg']} (code: {data['code']})")
        
        # 提取list数据
        employee_list = data['data'].get('list', [])
        
        # 提取id和employeeName
        result = []
        for employee in employee_list:
            if 'id' in employee and 'employeeName' in employee:
                result.append((employee['id'], employee['employeeName']))
            else:
                print(f"警告: 跳过缺少id或employeeName的项: {employee}")
        
        return result
        
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return []
    except json.JSONDecodeError:
        print(f"错误: 文件 {file_path} 不是有效的JSON格式")
        return []
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return []

if __name__ == "__main__":
    # 使用示例
    json_file = "/data/myproject/insert-asserts/employee_data.json"  # 替换为你的JSON文件路径
    employee_info = extract_employee_info(json_file)
    
    print("\n提取的员工信息:")
    print("ID\t\t\t\t\t员工姓名")
    print("=" * 60)
    for emp_id, emp_name in employee_info:
        print(f"{emp_id}\t{emp_name}")
    
    print(f"\n共提取了 {len(employee_info)} 条员工信息")

