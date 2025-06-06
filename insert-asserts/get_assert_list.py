import requests
import pandas as pd
from urllib.parse import urlencode

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

def send_request(url="", headers="", output_file=""):
    # 2. 发送 GET 请求
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        print(response.text)
        exit()

    # 3. 解析 JSON 数据
    json_data = response.json()

    if json_data.get("code") != 0:
        print(f"API 返回错误: {json_data.get('msg')}")
        exit()

    # 4. 提取数据（假设 list 里的每个 item 包含 id 和 employeeName）
    data_list = json_data["data"]["list"]
    extracted_data = []

    for item in data_list:
        extracted_data.append({
            "id": item.get("id", ""),
            "warehouseId": item.get("warehouseId", ""),   # 可选：提取其他字段
            "assetCode": item.get("assetCode", "")         # 可选：提取其他字段
        })

    # 5. 保存到 Excel
    df = pd.DataFrame(extracted_data)
    df.to_excel(output_file, index=False, engine="openpyxl")

    print(f"数据已保存到 {output_file}")
    print(f"共提取 {len(extracted_data)} 条记录")

if __name__ == '__main__':
    # 1. 设置请求 url 和 headers
    base_url = "https://devops-api.nullmax.net/asset/api/v1/fixed/list"
    params = {
        "page": 1,
        "pageSize": 282,
        "name": "",
        "warehouseId": "",
        "assetType": "",
        "assetCode": "",
        "categoryId": "C57228952616271872",
        "employeeId": "",
        "departmentId": "",
        "assetState": "",
        "isDelete": ""
    }

    url = f"{base_url}?{urlencode(params)}"

    headers = {
        "authority": "devops-api.nullmax.net",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE3ODk0MDAsImlhdCI6MTc0OTEzNzQwMCwiaXNzIjoi5ZSQ5L-K5ZacIiwicm9sZV9pZCI6IlI1NzIwMzc3NzcyMjE4NzgwOCIsInN1YiI6ImxvZ2luIiwidXNlcl9pZCI6IjQyNiIsIndhcmVob3VzZV9pZHMiOnsiVzU3MjAzNzcwMzA5NzM4NDk2IjoiVzU3MjAzNzcwMzA5NzM4NDk2In19.o-xpaDJj1wW8Xv8W2rUMIs5PMsF9ZhUz-s4alqEVCl8",
        "origin": "https://devops.nullmax.net",
        "referer": "https://devops.nullmax.net/",
        "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
    }
    output_file = "/home/ubuntu/Downloads/zj_info1.xlsx"
    send_request(url=url, headers=headers, output_file=output_file)