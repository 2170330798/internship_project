from datetime import datetime
import time
import requests
import json
import pandas as pd

def send_request(url=None, 
                 headers=None,
                 payload=None):
    try:
        # 发送POST请求
        response = requests.put(
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
                         sheet_name=None, is_save=False, skip_rows=0,
                         format_column=None, uppercase=False):
    """
    增强版Excel搜索工具：自动处理混合日期格式
    
    参数:
        input_file: 输入Excel文件路径
        output_file: 输出Excel文件路径
        search_column: 要搜索的列(列名或列索引)
        keyword: 要搜索的关键词
        sheet_name: 要处理的工作表名(可以是单个名称、索引、列表或None)
        is_save: 是否保存结果
        skip_rows: 跳过的行数
        format_column: 需要格式化的列(列名或列索引)
        uppercase: 是否将format_column列的内容转为大写
        
    date_columns: 需要转换的日期列（如["购入或入账日期"]），自动处理以下格式：
                  - Excel序列数字（如43101）
                  - 字符串日期（如"9/30/2018"）
                  - 空值自动转为NaT
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
                
                # 处理格式化列
                if format_column is not None and len(matched_rows) > 0:
                    if isinstance(format_column, int):
                        if format_column >= len(matched_rows.columns):
                            print(f"警告: 格式化列索引 {format_column} 超出范围")
                        else:
                            format_col_name = matched_rows.columns[format_column]
                    else:
                        if format_column not in matched_rows.columns:
                            print(f"警告: 格式化列名 '{format_column}' 不存在")
                        else:
                            format_col_name = format_column
                    
                    if 'format_col_name' in locals():
                        if uppercase:
                            matched_rows[format_col_name] = matched_rows[format_col_name].astype(str).str.upper()
                            print(f"已将列 '{format_col_name}' 内容转为大写")
                
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

def ensure_float(value):
    try:
        return float(value) if not isinstance(value, (float, int)) else float(value)
    except (ValueError, TypeError):
        raise ValueError(f"无法将{value}转换为浮点数")

def ensure_int(value):
    return int(value) if not isinstance(value, int) else value

def ensure_string(value, is_upper = False):
    if is_upper:
        return str(value).upper() if not isinstance(value, str) else value.upper()
    else :
        return str(value) if not isinstance(value, str) else value

def convert_date(date_str):
    if pd.isna(date_str) or date_str is None or date_str == "" or len(date_str) < 8:
        return "0000-00-00"  # 或者返回 None 或其他默认值
    # 解析前8位字符为日期
    date_obj = datetime.strptime(date_str[:8], "%Y%m%d").date()
    formatted_date = date_obj.strftime("%Y-%m-%d")
    #print(formatted_date)  # 输出: 2023-08-01
    return formatted_date

def set_payload(asset_amount = 0.0, #单价
                asset_code = "",  #资产编号
                asset_name = "",  #资产名称
                asset_type = 0,  #资产来源
                category_id = "", #资产类别ID
                asset_id = "",
                purchase_date = "", #资产购入/租赁日期
                serial_number = "", #资产序列号
                specifications = "", #资产型号
                warehouse_id = "", #仓库ID
                warranty_period_date = "", #质保期
                remark = "" #备注
    ):
    
    # 请求体数据
    payload = {
        "id": ensure_string(asset_id),
        "warehouseId": ensure_string(warehouse_id),
        "categoryId": ensure_string(category_id),
        "amount": ensure_float(asset_amount),
        "assetCode": ensure_string(asset_code),
        "assetImages": [],
        "assetName":  ensure_string(asset_name),
        "assetType": ensure_int(asset_type),
        "contact": "",
        "contactInfo": "",
        "purchaseDate": convert_date(ensure_string(purchase_date)),
        "remark": ensure_string(remark),
        "serialNumber": ensure_string(serial_number),
        "specifications": ensure_string(specifications),
        "supplierName": "",
        "warrantyPeriodDate": ensure_string(warranty_period_date)
    }


    return payload



import pandas as pd

def read_excel_sheet(file_path, sheet_name=None, columns=None):
    """
    读取Excel文件的指定sheet和列
    :param file_path: Excel文件路径
    :param sheet_name: sheet名称，如果为None则读取第一个sheet
    :param columns: 要读取的列，如果为None则读取所有列
    :return: DataFrame
    """
    if sheet_name is None:
        return pd.read_excel(file_path, usecols=columns)
    else:
        return pd.read_excel(file_path, sheet_name=sheet_name, usecols=columns)

def compare_and_save(file1_path, file1_sheet, file1_columns,
                     file2_path, file2_sheet, file2_columns,
                     compare_field1, compare_field2,
                     output_path):
    """
    比较两个Excel文件的指定字段并保存匹配结果
    :param file1_path: 第一个Excel文件路径
    :param file1_sheet: 第一个Excel文件的sheet名称
    :param file1_columns: 第一个Excel文件要读取的列
    :param file2_path: 第二个Excel文件路径
    :param file2_sheet: 第二个Excel文件的sheet名称
    :param file2_columns: 第二个Excel文件要读取的列
    :param compare_field1: 第一个Excel文件用于比较的字段名
    :param compare_field2: 第二个Excel文件用于比较的字段名
    :param output_path: 输出文件路径
    """
    # 读取第一个Excel文件
    df1 = read_excel_sheet(file1_path, file1_sheet, file1_columns)
    # 读取第二个Excel文件
    df2 = read_excel_sheet(file2_path, file2_sheet, file2_columns)
    
    # 将比较字段转换为大写
    df1[compare_field1] = df1[compare_field1].astype(str).str.upper()
    df2[compare_field2] = df2[compare_field2].astype(str).str.upper()
    
    # 合并两个DataFrame，基于比较字段
    merged_df = pd.merge(df1, df2, left_on=compare_field1, right_on=compare_field2, how='inner')
    
    # 选择要保存的列
    # 表1的字段：编号(比较字段)、资产型号名称、验收编号、序列号
    # 表2的字段：id、warehouseId
    # 确保这些字段都存在
    required_columns = [
        compare_field1,  # 表1的编号
        '资产型号名称', '验收编号', '序列号',  # 表1的其他字段
        'id', 'warehouseId'  # 表2的字段
    ]
    
    # 检查merged_df中是否有所需的列
    available_columns = [col for col in required_columns if col in merged_df.columns]
    
    if not available_columns:
        print("错误：合并后的DataFrame中没有所需的列")
        return
    
    # 保存到新的Excel文件
    merged_df[available_columns].to_excel(output_path, index=False)
    print(f"匹配结果已保存到: {output_path}")




if __name__ == "__main__":

    # 购入
    PURCHASE = 1
    # 租赁
    RENT = 2
    # 赠送
    DONATE = 3
    # 设置来源
    WAY = PURCHASE
    
    # 设置开头无效数据行数
    skip_rows = 0
    # 设置发送间隔时间
    delay_time = 1 # 1s
    # 设置文件参数
    input_excle_file_dir = "/home/ubuntu/Downloads"
    input_excle_file_name = "assets_list.xlsx"
    output_excel_file_dir = "/home/ubuntu/Downloads"  
    output_excel_file_name = "zj_info.xlsx"
    column_to_search = 0             # 可以是列名(如"姓名")或列索引(从0开始）
    search_keyword = ""           # 要搜索的关键字
    sheet_name = "主机"      # 查找的表

    # 设置请求URL
    url = "https://devops-api.nullmax.net/asset/api/v1/fixed"

    # 设置请求头
    
    headers = {
        "authority": "devops-api.nullmax.net",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE3MTI1ODUsImlhdCI6MTc0OTA2MDU4NSwiaXNzIjoi5ZSQ5L-K5ZacIiwicm9sZV9pZCI6IlI1NzIwMzc3NzcyMjE4NzgwOCIsInN1YiI6ImxvZ2luIiwidXNlcl9pZCI6IjQyNiIsIndhcmVob3VzZV9pZHMiOnsiVzU3MjAzNzcwMzA5NzM4NDk2IjoiVzU3MjAzNzcwMzA5NzM4NDk2In19.jmHb1DCQR0e_EVgpC4uQvJHIqH3vPe1LaoWMDFTzhWw",
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

    
    '''
    "categoryId": 类别ID
        "C57228951773609984" --> 笔记本
        "C57228952616271872" --> 主机
        "C57231373712162816" --> 显示器
        "C57228956114354176" --> 移动硬盘
        "C57228956763357184" --> 办公网络设备
        "C57229182348394496" --> 办公其他设备
        ...
    '''

    # # 配置参数
    # file1_path = '/home/ubuntu/Downloads/assets_list.xlsx'  # 第一个Excel文件路径
    # file1_sheet = '笔记本'  # 第一个Excel文件的sheet名称
    # file1_columns = ['编号', '资产型号名称', '验收编号', '序列号']  # 第一个Excel文件要读取的列
    
    # file2_path = '/home/ubuntu/Downloads/bjb_info.xlsx'  # 第二个Excel文件路径
    # file2_sheet = 'Sheet1'  # 第二个Excel文件的sheet名称
    # file2_columns = ['id', 'warehouseId', 'assetCode']  # 第二个Excel文件要读取的列
    
    # compare_field1 = '编号'  # 第一个Excel文件用于比较的字段名
    # compare_field2 = 'assetCode'  # 第二个Excel文件用于比较的字段名
    
    # output_path = '/home/ubuntu/Downloads/merge_info7.xlsx'  # 输出文件路径
    
    # # 执行比较和保存
    # compare_and_save(file1_path, file1_sheet, file1_columns,
    #                 file2_path, file2_sheet, file2_columns,
    #                 compare_field1, compare_field2,
    #                 output_path)




    
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
        is_save=False,
        skip_rows=skip_rows,
        format_column=None, 
        uppercase=False
    )

    for index, row in asset_data.iterrows():
        # 购入
        if WAY == PURCHASE:
            print(f"资产编号: {str(row['主机编号']).upper()}, 使用状态: {str(row['使用状态'])}, 使用人: {str(row['使用人 (人员 )'])}")
            #print(f"资产编号: {row['编号']},	资产名称: {row['资产型号名称']}, 购入或入账日期: {convert_date(ensure_string(row['验收编号']))}, S/N码: {row['序列号']}, 资产ID: {row['id']}, 仓库ID:{row['warehouseId']}")
            #print(f"资产名称: {row['资产型号名称']},  型号: {row['资产型号名称']}, S/N码: {row['序列号']}  购入或入账日期: {convert_date(ensure_string(row['验收编号']))}, 资产编号: {ensure_string(row['编号'], True)}")
            payload = set_payload(asset_amount = 0.0, 
                                  asset_code = row['编号'], 
                                  asset_name = row['资产型号名称'], 
                                  asset_type = 1, 
                                  category_id = "C57228951773609984",
                                  asset_id= row['id'], 
                                  purchase_date = row['验收编号'], 
                                  serial_number = row['序列号'], 
                                  specifications = row['资产型号名称'], 
                                  warehouse_id = "W57203770309738496", 
                                  warranty_period_date = "",
                                  remark= "")
        elif WAY == RENT:
             # 租赁
            print(f"资产名称: {row['资产名称']},  型号: {row['型号']},  租赁日期: {row['租赁日期']}, S/N号: {row['S/N号']}, 资产编号: {row['资产编号']}")
            payload = set_payload(asset_amount = 0.0, 
                                  asset_code = row['资产编号'], 
                                  asset_name = row['资产名称'], 
                                  asset_type = 2, 
                                  category_id = "C57229559082188800", 
                                  purchase_date = row['租赁日期'], 
                                  serial_number = row['S/N号'], 
                                  specifications = row['型号'],
                                  warehouse_id = "W57203770309738496", 
                                  warranty_period_date = "",
                                  remark="")
        elif WAY == DONATE:
            # 捐赠
            print(f"资产名称: {row['资产名称']},  型号: {row['型号']},  购入或入账日期: {row['登陆日期']}, S/N号: {ensure_string(row['S/N号'])}, 资产编号: {row['资产编号']}")
            payload = set_payload(asset_amount = 0.0, 
                                  asset_code = row['资产编号'], 
                                  asset_name = row['资产名称'], 
                                  asset_type = 3, 
                                  category_id = "C57229558494593024", 
                                  purchase_date = row['登陆日期'], 
                                  serial_number = row['S/N号'], 
                                  specifications = row['型号'], 
                                  warehouse_id = "W57203770309738496", 
                                  warranty_period_date = "",
                                  remark="岩山赠与")
        # print(payload)
        # send_request(url, headers, payload)
        # time.sleep(delay_time)  # 休眠1秒
        


