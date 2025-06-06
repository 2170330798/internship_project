# import pandas as pd
# from datetime import datetime
# import re

# def convert_excel_date(date_str):
#     """
#     优化版日期转换函数：
#     1. 只处理前12位数字作为日期时间（年月日时分）
#     2. 忽略后面所有字符
#     3. 严格验证日期有效性
#     """
#     if pd.isna(date_str):
#         return None
    
#     # 转为字符串并清理
#     date_str = str(date_str).strip()
    
#     # 提取前12位数字（忽略后面所有内容）
#     digits = re.sub(r'[^\d]', '', date_str)[:12]  # 只取前12位数字
    
#     # 检查是否为12位数字
#     if len(digits) != 12 or not digits.isdigit():
#         return None
    
#     # 分离日期时间组件
#     year = int(digits[0:4])
#     month = int(digits[4:6])
#     day = int(digits[6:8])
    
#     try:
#         # 创建日期对象验证有效性（忽略时分部分）
#         dt = datetime(year, month, day)
#         return dt.strftime("%Y-%m-%d")
#     except ValueError:
#         return None

# # 读取Excel文件
# df = pd.read_excel('/home/ubuntu/Downloads/output7.xlsx')  # 替换为实际文件路径

# # 打印列名确认
# print("文件中存在的列名有：")
# print(df.columns.tolist())

# # 假设日期列实际名为"验收编号"，请根据实际情况调整
# date_column = '验收编号'  # 修改为您实际的日期列名

# # 转换日期列
# df['验收编号'] = df[date_column].apply(convert_excel_date)

# # 统计转换结果
# total_count = len(df)
# success_count = df['验收编号'].notna().sum()
# fail_count = total_count - success_count

# print(f"\n转换统计：")
# print(f"总行数: {total_count}")
# print(f"成功转换: {success_count}")
# print(f"转换失败: {fail_count}")

# # 查看转换失败的样本（前5条）
# if fail_count > 0:
#     print("\n转换失败的样本：")
#     print(df[df['验收编号'].isna()][[date_column]].head(5))

# print(df)

# from openpyxl import load_workbook
# excle_file_path = "/home/ubuntu/Downloads"
# excle_file_name = "server_list.xlsx"
# wb = load_workbook(excle_file_path+'/'+excle_file_name)
# sheet = wb.active

# # 跳过前两行，第 3 行是列名
# headers = [cell.value for cell in sheet[3]]  # 第 3 行是列名
# data = []

# for row in sheet.iter_rows(min_row=4, values_only=True):  # 从第 4 行开始读取数据
#     data.append(row)

# print("列名:", headers)
# print("第一行数据:", data[0])  # 第一行数据

import pandas as pd
from datetime import datetime

def convert_date(date_str):
    if pd.isna(date_str) or date_str is None or date_str == "":
        return ""  # 或者返回 None 或其他默认值
    # 解析前8位字符为日期
    date_obj = datetime.strptime(date_str[:8], "%Y%m%d").date()
    formatted_date = date_obj.strftime("%Y-%m-%d")
    #print(formatted_date)  # 输出: 2023-08-01
    return formatted_date

print(convert_date("202211250019"))