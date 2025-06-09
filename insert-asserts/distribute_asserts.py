import math
import requests
import json
import pandas as pd
import time

def send_request(url="", headers="", payload=""):
    try:
        # 发送PUT请求
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        
        # 检查响应状态码
        if response.status_code == 200:
            print("资产信息更新成功！")
            print("响应内容:", response.json())
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print("响应内容:", response.text)
    
    except requests.exceptions.RequestException as e:
        print("请求发生错误:", e)

def ensure_string(value):
    return str(value) if not isinstance(value, str) else value

def ensure_float(value):
    try:
        return float(value) if not isinstance(value, (float, int)) else float(value)
    except (ValueError, TypeError):
        raise ValueError(f"无法将{value}转换为浮点数")

def ensure_int(value):
     if pd.isna(value) or (isinstance(value, float) and math.isnan(value)):
        return 0  # 或者返回一个默认值如 0
     else:
        return int(value) if not isinstance(value, int) else value


def update_asset_allocation(asset_id="", employee_id="", warehouse_id="", remark=""):
    """
    更新资产分配信息
    
    参数:
        asset_id (str): 资产ID
        employee_id (str): 员工ID
        warehouse_id (str): 仓库ID
        remark (str): 备注信息，默认为空字符串
    """
    # API端点
    url = "https://devops-api.nullmax.net/asset/api/v1/fixed/transfer/reallocate"
    
    # 请求头
    headers = {
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTIwMjg0NDksImlhdCI6MTc0OTM3NjQ0OSwiaXNzIjoi5ZSQ5L-K5ZacIiwicm9sZV9pZCI6IlI1NzIwMzc3NzcyMjE4NzgwOCIsInN1YiI6ImxvZ2luIiwidXNlcl9pZCI6IjQyNiIsIndhcmVob3VzZV9pZHMiOnsiVzU3MjAzNzcwMzA5NzM4NDk2IjoiVzU3MjAzNzcwMzA5NzM4NDk2In19.HN41JNNFTBZu0blroR8kkAjHjUTRMppZ611adaTQZ2A",
        "Content-Type": "application/json",
        "Origin": "https://devops.nullmax.net",
        "Referer": "https://devops.nullmax.net/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "Warehouse": "W57203770309738496",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    # 请求体
    payload = {
        "id": ensure_string(asset_id),
        "employeeId": ensure_string(ensure_int(employee_id)),
        "warehouseId": ensure_string(warehouse_id),
        "remark": ensure_string(remark)
    }
    print(payload)
    send_request(url=url, headers=headers, payload=payload)

def read_excel_sheet(file_path, sheet_name=None, columns=None, condition_column=None, condition_value=None):
    """
    读取Excel表格的指定sheet和列，并可选择根据条件筛选
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        if sheet_name is not None and isinstance(df, dict):
            df = df[sheet_name]
        
        # 筛选条件
        #if condition_column and condition_value:
        #    df = df[df[condition_column] == condition_value]
        # 执行搜索
        if condition_column and condition_value:
            df = df[df[condition_column].astype(str).str.contains(condition_value, case=False, na=False)]
    
        # 选择指定列
        if columns:
            df = df[columns]
        
        return df
    except Exception as e:
        print(f"读取Excel文件出错: {e}")
        return None

def compare_and_merge(table1_path, table1_sheet, table1_columns, table1_status_column, table1_status_value,
                     table2_path, table2_sheet, table2_columns,
                     table3_path=None, table3_sheet=None, table3_columns=None,
                     output_path="output.xlsx"):
    """
    比较并合并表格数据
    """
    # 读取表1
    table1 = read_excel_sheet(table1_path, table1_sheet, table1_columns, 
                             table1_status_column, table1_status_value)
    if table1 is None:
        return
    
    # 读取表2
    table2 = read_excel_sheet(table2_path, table2_sheet, table2_columns)
    if table2 is None:
        return
    
    # 读取表3（如果有）
    table3 = None
    if table3_path and table3_sheet and table3_columns:
        table3 = read_excel_sheet(table3_path, table3_sheet, table3_columns)
    
    # 确保表1有'编号'列，表2有'assetCode'列
    if '编号' not in table1.columns or 'assetCode' not in table2.columns:
        print("表1缺少'编号'列或表2缺少'assetCode'列")
        return
    
    # 比较并合并表1和表2
    # 将比较字段转为大写
    table1['编号'] = table1['编号'].astype(str).str.upper() 
    table2['assetCode'] = table2['assetCode'].astype(str).str.upper()
    
    # 合并表1和表2
    merged = pd.merge(table1, table2, 
                      left_on='编号', 
                      right_on='assetCode',
                      how='inner')
    
    # 选择需要的列
    result_columns = []
    if '使用人 (人员 )' in merged.columns:
        result_columns.append('使用人 (人员 )')
    if 'id' in merged.columns:
        result_columns.append('id')
    if 'warehouseId' in merged.columns:
        result_columns.append('warehouseId')
    if '编号' in merged.columns:
        result_columns.append('编号')
    
    if not result_columns:
        print("没有找到需要的列")
        return
    
    result = merged[result_columns]
    
    # 如果有表3，处理员工ID映射
    if table3 is not None and 'employeeName' in table3.columns and 'id' in table3.columns:
        # 重命名表3的id列为employeeId，避免与表2的id列冲突
        table3 = table3.rename(columns={'id': 'employeeId'})
        
        # 合并员工ID信息
        result = pd.merge(result, table3, 
                          left_on='使用人 (人员 )', 
                          right_on='employeeName',
                          how='left')
        
        # 替换使用人 (人员 2)为employeeId
        result['employeeId'] = result['employeeId'].fillna(result['使用人 (人员 )'])
        result = result.drop(columns=['使用人 (人员 )', 'employeeName'], errors='ignore')
    
    # 保存结果
    try:
        result.to_excel(output_path, index=False)
        print(f"结果已保存到 {output_path}")
    except Exception as e:
        print(f"保存结果出错: {e}")


def search_and_save_excel(input_file, output_file, search_column, keyword, 
                         sheet_name=None, is_save=False, skip_rows=0):
    """
    增强版Excel搜索工具：自动处理混合日期格式
    
    参数:
        date_columns: 需要转换的日期列（如["购入或入账日期"]），自动处理以下格式：
                      - Excel序列数字（如43101）
                      - 字符串日期（如"9/30/2018"）
                      - 空值自动转为NaT
        skip_rows: 跳过前面多少行无效值
    """
    
    try:
        xls = pd.ExcelFile(input_file)
        all_sheets = xls.sheet_names
        
        # 处理sheet_name参数
        if sheet_name is None:
            sheets_to_process = [all_sheets[0]]
        elif isinstance(sheet_name, (int, str)):
            sheets_to_process = [sheet_name]
        elif isinstance(sheet_name, list):
            sheets_to_process = sheet_name
        else:
            raise ValueError("sheet_name参数必须是工作表名、索引、列表或None")
        
        all_matched_rows = []
        
        for sheet in sheets_to_process:
            try:
                # 读取数据（跳过前两行）
                df = pd.read_excel(input_file, sheet_name=sheet, header=skip_rows)
                print(f"\n处理工作表: '{sheet}' (共 {len(df)} 行)")
                
                # 处理搜索列
                if isinstance(search_column, int):
                    if search_column >= len(df.columns):
                        print(f"警告: 列索引 {search_column} 超出范围")
                        continue
                    column = df.columns[search_column]
                else:
                    if search_column not in df.columns:
                        print(f"警告: 列名 '{search_column}' 不存在，可用列: {list(df.columns)}")
                        continue
                    column = search_column
                
                # 执行搜索
                matched_rows = df[df[column].astype(str).str.contains(keyword, case=False, na=False)]
                
                if len(matched_rows) > 0:
                    print(f"✅ 找到 {len(matched_rows)} 行匹配内容")
                    matched_rows['来源工作表'] = sheet
                    all_matched_rows.append(matched_rows)
                
            except Exception as e:
                print(f"处理工作表 '{sheet}' 时出错: {str(e)}")
                continue
        
        if not all_matched_rows:
            print(f"\n未找到包含 '{keyword}' 的行")
            return None
        
        final_result = pd.concat(all_matched_rows, ignore_index=True)
        
        # 保存结果
        if is_save:
            try:
                final_result.to_excel(output_file, index=False)
                print(f"\n💾 已保存 {len(final_result)} 行到 {output_file}")
            except Exception as e:
                print(f"保存失败: {str(e)}")
        
        return final_result
    
    except Exception as e:
        print(f"全局错误: {str(e)}")
        return None

# 示例使用
if __name__ == "__main__":
    # # 表1配置
    # table1_path = "/home/ubuntu/Downloads/assets_list.xlsx"
    # table1_sheet = "其他"  # 指定sheet名称或None使用第一个sheet
    # table1_columns = ["编号", "使用人 (人员 )", "说明"]  # 要读取的列
    # table1_status_column = "说明"  # 筛选条件的列
    # table1_status_value = "其他设备"  # 筛选条件的值
    
    # # 表2配置
    # table2_path = "/home/ubuntu/Downloads/orthers_info1.xlsx"
    # table2_sheet = "Sheet1"  # 指定sheet名称或None使用第一个sheet
    # table2_columns = ["id", "warehouseId", "assetCode"]  # 要读取的列
    
    # # 表3配置（可选）
    # table3_path = "/home/ubuntu/Downloads/employee_info.xlsx"  # 设为None如果不使用表3
    # table3_sheet = "Sheet1"  # 指定sheet名称或None使用第一个sheet
    # table3_columns = ["id", "employeeName"]  # 要读取的列
    
    # # 输出文件路径
    # output_path = "/home/ubuntu/Downloads/merge_info12.xlsx"
    
    # # 执行比较和合并
    # compare_and_merge(
    #     table1_path, table1_sheet, table1_columns, table1_status_column, table1_status_value,
    #     table2_path, table2_sheet, table2_columns,
    #     table3_path, table3_sheet, table3_columns,
    #     output_path
    # )

    # 设置延迟时间
    delay_time = 1
    # 设置文件参数
    input_excle_file_dir = "/home/ubuntu/Downloads"
    input_excle_file_name = "merge_info12.xlsx"
    # output_excel_file_dir = "/home/ubuntu/Downloads"  
    # output_excel_file_name = "low_network_switch.xlsx"
    column_to_search = 0           # 可以是列名(如"姓名")或列索引( 从0开始)
    search_keyword = ""           # 要搜索的关键字
    sheet_name = "Sheet1"      # 查找的表
    skip_rows = 0
    asset_data = search_and_save_excel(
        input_file=input_excle_file_dir+'/'+input_excle_file_name, 
        output_file=None, 
        search_column=column_to_search, 
        keyword=search_keyword,
        sheet_name=sheet_name, # 可以修改为上面注释中的任意一种形式
        is_save=False,
        skip_rows = skip_rows
    )
    
    for index, row in asset_data.iterrows():
        print(f"资产ID: {row['id']},  仓库ID: {row['warehouseId']},  使用人: {ensure_int(row['employeeId'])},  资产编号: {row['编号']}")
        # 替换为实际的资产ID、员工ID和仓库ID
        # asset_id = "AF57232242631508000"
        # employee_id = "454"
        # warehouse_id = "W57203770309738496"
        # remark = "资产重新分配"
        update_asset_allocation(row['id'], row['employeeId'], row['warehouseId'], remark="")
        time.sleep(delay_time)  # 休眠1秒

