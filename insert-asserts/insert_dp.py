import re
import time
import requests
import json
from datetime import datetime
import pandas as pd


        
def read_excel_with_actual_columns(file_path):
    try:
        # 1. 读取整个文件
        df = pd.read_excel(file_path)
        df = df.fillna("")

        # 2. 打印所有列名供参考
        print("文件中存在的列名有：")
        print(df.columns.tolist())
        
        # 3. 定义要读取的列名列表
        columns_to_read = [
            "编号",
            "验收编号",
            "来源工作表"
        ]
        
        # 4. 检查哪些列实际存在
        existing_columns = [col for col in columns_to_read if col in df.columns]
        missing_columns = set(columns_to_read) - set(existing_columns)
        
        if missing_columns:
            print(f"警告: 以下列不存在于文件中: {missing_columns}")
        
        # 5. 筛选需要的列
        df = df[existing_columns]

        # 6. 数据处理
        if "编号" in df.columns:
            df["编号"] = df["编号"].astype(str).str.upper()

        if "验收编号" in df.columns:
            # 先转换为字符串，然后处理浮点数情况
            df["验收编号"] = df["验收编号"].astype(str)
            # 移除末尾的.0（如果有）
            df["验收编号"] = df["验收编号"].str.replace(r'\.0$', '', regex=True)
            # 将空字符串替换为None或保持为空字符串
            df["验收编号"] = df["验收编号"].replace('', None)  # 或 replace('', '')
            

        return df
        
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None

def convert_date(date_str):
    if pd.isna(date_str) or date_str is None or date_str == "":
        return ""  # 或者返回 None 或其他默认值
    # 解析前8位字符为日期
    date_obj = datetime.strptime(date_str[:8], "%Y%m%d").date()
    formatted_date = date_obj.strftime("%Y-%m-%d")
    #print(formatted_date)  # 输出: 2023-08-01
    return formatted_date
    
# if __name__ == "__main__":
    
#     excel_file = "/home/ubuntu/Downloads/output7.xlsx"  # 替换为你的 Excel 文件路径
    
#     asset_data = read_excel_with_actual_columns(excel_file)
#     for index, row in asset_data.iterrows():
#         print(f"资产名称: {row['来源工作表']},  购入或入账日期: {convert_date(row['验收编号'])}  ,资产编码: {row['编号']}")
        

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
  


if __name__ == "__main__":
    # 请求URL
    url = "https://devops-api.nullmax.net/asset/api/v1/fixed"

    # 请求头
    headers = {
        "authority": "devops-api.nullmax.net",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE1MTI0ODAsImlhdCI6MTc0ODg2MDQ4MCwiaXNzIjoi5ZSQ5L-K5ZacIiwicm9sZV9pZCI6IlI1NzIwMzc3NzcyMjE4NzgwOCIsInN1YiI6ImxvZ2luIiwidXNlcl9pZCI6IjQyNiIsIndhcmVob3VzZV9pZHMiOnsiVzU3MjAzNzcwMzA5NzM4NDk2IjoiVzU3MjAzNzcwMzA5NzM4NDk2In19.EslJMrFJvXwQR5cox62JPZ1HPj437Hqk-AuARW34I9w",
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

    # 请求体数据
    payload = {
        "warehouseId": "W57203770309738496",
        "categoryId": "C57231373712162816",
        "assetCode": "",
        "assetName": "",
        "assetType": 1,
        "purchaseDate": "",
        "warrantyPeriodDate": ""
    }
    excel_file = "/home/ubuntu/Downloads/output7.xlsx"  # 替换为你的 Excel 文件路径
    
    asset_data = read_excel_with_actual_columns(excel_file)
    for index, row in asset_data.iterrows():
        print(f"资产名称: {row['来源工作表']},  购入或入账日期: {convert_date(row['验收编号'])}  ,资产编码: {row['编号']}")
        payload["assetCode"] = row["编号"]
        payload["assetName"] = row["来源工作表"]
        payload["purchaseDate"] = convert_date(row['验收编号']) if row['验收编号'] else "2021-01-01"
        print(payload)
        send_request(url, headers, payload)
        time.sleep(1)  # 休眠1秒
        