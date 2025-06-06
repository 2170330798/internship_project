import pandas as pd
import json
from typing import List, Tuple

def extract_employee_info(file_path: str) -> List[Tuple[str, str]]:
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

def create_name_id_mapping(employee_info: List[Tuple[str, str]]) -> dict:
    """
    创建姓名到ID的映射字典
    
    :param employee_info: 包含(id, name)元组的列表
    :return: {姓名: ID}的字典
    """
    return {name: emp_id for emp_id, name in employee_info}

def process_excel_data(df: pd.DataFrame, name_id_map: dict) -> pd.DataFrame:
    """
    处理Excel数据，替换"使用人 (人员 2)"列为对应的ID
    
    :param df: 原始DataFrame
    :param name_id_map: 姓名到ID的映射字典
    :return: 处理后的DataFrame
    """
    if "使用人 (人员 2)" not in df.columns:
        print("Excel文件中没有'使用人 (人员 2)'列")
        return df
    
    print("开始处理'使用人 (人员 2)'列...")
    
    # 对每个"使用人 (人员 2)"查找ID
    df["使用人 (人员 2)"] = df["使用人 (人员 2)"].apply(
        lambda x: name_id_map.get(str(x).strip(), x) if pd.notna(x) else x
    )
    
    print("处理完成！")
    return df

def main():
    # 配置文件路径
    json_file = "/data/myproject/insert-asserts/employee_data.json"  # 员工数据JSON文件
    excel_input = "/home/ubuntu/Downloads/output5.xlsx"       # 输入Excel文件
    excel_output = "/home/ubuntu/Downloads/output6.xlsx"     # 输出Excel文件
    
    # 步骤1: 从JSON提取员工信息
    print("从JSON文件提取员工信息...")
    employee_info = extract_employee_info(json_file)
    
    if not employee_info:
        print("无法获取员工信息，程序终止")
        return
    
    # 步骤2: 创建姓名-ID映射
    name_id_map = create_name_id_mapping(employee_info)
    print(f"成功创建 {len(name_id_map)} 条员工姓名-ID映射")
    
    # 步骤3: 读取并处理Excel文件
    try:
        print(f"读取Excel文件: {excel_input}")
        df = pd.read_excel(excel_input)
        
        # 步骤4: 替换姓名列为ID
        processed_df = process_excel_data(df, name_id_map)
        
        # 步骤5: 保存结果
        processed_df.to_excel(excel_output, index=False)
        print(f"处理后的文件已保存到: {excel_output}")
        
    except Exception as e:
        print(f"处理Excel文件时出错: {e}")

if __name__ == "__main__":
    main()