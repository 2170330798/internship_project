from datetime import datetime
import time
import numpy as np
import requests
import json
import pandas as pd

def send_request(url=None, 
                 headers=None,
                 payload=None):
    try:
        # 发送POST请求
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),  # 将字典转换为JSON字符串
            verify=True  # 验证SSL证书
        )

        # 打印响应信息
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        print("\nResponse Body:")
        print(response.text)

        # 如果需要处理JSON响应
        if "application/json" in response.headers.get("content-type", ""):
            response_json = response.json()
            print("\nJSON Response:")
            print(json.dumps(response_json, indent=2, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

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

def convert_date_to_short_string(date):
    """
    将 row["购入或入账日期"] 从 "2025-05-30 00:00:00" 转为 "2025-05-30"
    
    参数:
        row: pandas DataFrame 的某一行（包含日期列）
    
    返回:
        str: 格式化后的日期字符串（如 "2025-05-30"）
    """
    if pd.isna(date):
        return ""  # 处理空值
    
    # 如果已经是 datetime 对象，直接格式化
    if isinstance(date, (pd.Timestamp, datetime)):
        return date.strftime("%Y-%m-%d")
    
    # 如果是字符串，先转为 datetime 再格式化
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return "0000-00-00"  # 如果格式不符，返回0000-00-00
    
    

def convert_date(date_str):
    if pd.isna(date_str) or date_str is None or date_str == "" or len(date_str) < 8:
        return "0000-00-00"  # 或者返回 None 或其他默认值
    # 解析前8位字符为日期
    date_obj = datetime.strptime(date_str[:8], "%Y%m%d").date()
    formatted_date = date_obj.strftime("%Y-%m-%d")
    #print(formatted_date)  # 输出: 2023-08-01
    return formatted_date

def clean_value(value):
    """安全处理单个值中的NaN，返回字符串或原值"""
    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return ""
    elif value != value:  # 捕获所有NaN类型
        return ""
    else:
        return str(value)  # 确保返回字符串

def ensure_string(value):
    return str(value) if not isinstance(value, str) else value

def ensure_float(value):
    try:
        return float(value) if not isinstance(value, (float, int)) else float(value)
    except (ValueError, TypeError):
        raise ValueError(f"无法将{value}转换为浮点数")

def ensure_int(value):
    return int(value) if not isinstance(value, int) else value

def set_payload(asset_amount = 0.0, #单价
                asset_code = "",  #资产编号
                asset_name = "",  #资产名称
                asset_type = 0,  #资产来源
                category_id = "", #资产类别ID
                purchase_date = "", #资产购入/租赁日期
                serial_number = "", #资产序列号
                specifications = "", #资产型号
                warehouse_id = "", #仓库ID
                warranty_period_date = "", #质保期
                remark = "" #备注
    ):
    
    # 请求体数据
    payload = {
        "amount": ensure_float(asset_amount),
        "assetCode": ensure_string(asset_code),
        "assetName": ensure_string(asset_name),
        "assetType": ensure_int(asset_type),
        "categoryId":  ensure_string(category_id),
        "purchaseDate": convert_date(ensure_string(purchase_date)),
        "serialNumber": ensure_string(serial_number),
        "specifications": ensure_string(specifications),
        "warehouseId": ensure_string(warehouse_id),
        "warrantyPeriodDate": ensure_string(warranty_period_date),
        "remark": ensure_string(remark)
    }

    return payload

if __name__ == "__main__":

    # 购入
    PURCHASE = 1
    # 租赁
    RENT = 2
    # 赠送
    DONATE = 3
    # 设置来源
    WAY = PURCHASE
    # 设置跳过前面几行
    skip_rows = 0
    # 设置发送间隔时间
    delay_time = 1 # 1s
    # 设置文件参数
    input_excle_file_dir = "/home/ubuntu/Downloads"
    input_excle_file_name = "assets_list.xlsx"
    output_excel_file_dir = "/home/ubuntu/Downloads"  
    output_excel_file_name = "work_network_switch.xlsx"
    column_to_search = 0             # 可以是列名(如"姓名")或列索引(从0开始)
    search_keyword = ""           # 要搜索的关键字
    sheet_name = "网络设备及小型设备"      # 查找的表

    # 设置请求URL
    url = "https://devops-api.nullmax.net/asset/api/v1/fixed"

    # 设置请求头
    headers = {
        "authority": "devops-api.nullmax.net",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE1OTQwOTksImlhdCI6MTc0ODk0MjA5OSwiaXNzIjoi5ZSQ5L-K5ZacIiwicm9sZV9pZCI6IlI1NzIwMzc3NzcyMjE4NzgwOCIsInN1YiI6ImxvZ2luIiwidXNlcl9pZCI6IjQyNiIsIndhcmVob3VzZV9pZHMiOnsiVzU3MjAzNzcwMzA5NzM4NDk2IjoiVzU3MjAzNzcwMzA5NzM4NDk2In19.T-zlIM_pevVLjQsi5u2OnnijeJNNdXhkIFMaRW2MBj0",
        "content-type": "application/json",
        "origin": "https://devops.nullmax.net",
        "referer": "https://devops.nullmax.net/",
        "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36", 
        "warehouse": "W57203770309738496"
    }
    
    # 资产类别ID：
    # 防火墙 C57252155105706016
    # 交换机 C57252155567734816
    # 办公网络设备 C57228956763357184
    
    # 指定要搜索的工作表(可选):
    # sheet_to_search = None       # 搜索第一个工作表(默认)
    # sheet_to_search = "Sheet1"   # 搜索指定名称的工作表
    # sheet_to_search = 1          # 搜索第二个工作表(索引从0开始)
    # sheet_to_search = ["Sheet1", "Sheet2"]  # 搜索多个工作表
    asset_data = search_and_save_excel(
        input_file=input_excle_file_dir+'/'+input_excle_file_name, 
        output_file=output_excel_file_dir+'/'+output_excel_file_name, 
        search_column=column_to_search, 
        keyword=search_keyword,
        sheet_name=sheet_name, # 可以修改为上面注释中的任意一种形式
        is_save=True,
        skip_rows = skip_rows
    )
    
    for index, row in asset_data.iterrows():
        # 购入设备
        if WAY == PURCHASE:
            print(f"资产名称: {row['物品描述']},  型号: {row['物品描述']},  购入或入账日期: {convert_date(ensure_string(row['验收编号']))}, S/N号: {row['S/N号']}, 资产编号: {row['资产编号']}")
            payload = set_payload(asset_amount = 0.0, 
                                  asset_code = row['资产编号'], 
                                  asset_name = row['物品描述'], 
                                  asset_type = 1, 
                                  category_id = "C57228956763357184", 
                                  purchase_date = row['验收编号'], 
                                  serial_number = row['S/N号'], 
                                  specifications = row['物品描述'], 
                                  warehouse_id = "W57203770309738496", 
                                  warranty_period_date = "",
                                  remark="")

        elif WAY == RENT:
             # 租赁设备
            print(f"资产名称: {row['资产名称']},  型号: {row['型号']},  租赁日期: {convert_date_to_short_string(row['租赁日期'])}, S/N号: {clean_value(row['S/N号'])}, 资产编号: {row['资产编号']}")
            payload = set_payload(asset_amount = 0.0, 
                                  asset_code = row['资产编号'], 
                                  asset_name = row['资产名称'], 
                                  asset_type = 2, 
                                  category_id = "C57229559082188800", 
                                  purchase_date = row['租赁日期'], 
                                  serial_number = row['S/N号'], 
                                  specifications = row['型号'],
                                  warehouse_id = "W57203770309738496", 
                                  warranty_period_date = "")
        elif WAY == DONATE:
            # 赠送
            print(f"资产名称: {row['资产名称']},  型号: {row['型号']},  购入或入账日期: {row['购入或入账日期']}, S/N号: {row['S/N号']}, 资产编号: {row['资产编号']}")
            payload = set_payload(asset_amount = 0.0, 
                                  asset_code = row['资产编号'], 
                                  asset_name = row['资产名称'], 
                                  asset_type = 3, 
                                  category_id = "C57252155567734816", 
                                  purchase_date = row['购入或入账日期'], 
                                  serial_number = row['S/N号'], 
                                  specifications = row['型号'], 
                                  warehouse_id = "W57203770309738496", 
                                  warranty_period_date = "",
                                  remark="岩山赠与")

        print(payload)
        send_request(url, headers, payload)
        time.sleep(delay_time)  # 休眠1秒
        


