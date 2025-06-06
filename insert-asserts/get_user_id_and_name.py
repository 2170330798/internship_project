import json
import pandas as pd

def save_id_and_name(input_json_file="", output_file=""):
    # 1. 读取 JSON 文件
    with open(input_json_file, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # 2. 提取 id 和 employeeName
    employees = json_data['data']['list']
    data = []
    for emp in employees:
        data.append({
            'id': emp['id'],
            'employeeName': emp['employeeName']
        })

    # 3. 转换为 DataFrame 并保存到 Excel
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

    print("数据已保存到: "+output_file)

if __name__ == '__main__':
    save_id_and_name("/data/myproject/insert-asserts/employee_data.json", "/home/ubuntu/Downloads/employee_info.xlsx")