from datetime import datetime
import os
import pandas as pd

def search_and_save_excel(input_file, output_file, search_column, keyword, 
                         sheet_name=None, is_save=False, skip_rows=0,
                         format_column=None, uppercase=False,
                         append_mode=False):
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
        append_mode: 是否追加到现有文件(False则覆盖原文件)
        
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
                if append_mode and os.path.exists(output_file):
                    # 读取现有文件内容
                    existing_data = pd.read_excel(output_file)
                    # 合并新旧数据
                    final_result = pd.concat([existing_data, final_result], ignore_index=True)
                    print("\n🔁 已追加到现有文件内容")
                
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
    output_excel_file_name = "zj_info2.xlsx"
    column_to_search = 0             # 可以是列名(如"姓名")或列索引(从0开始）
    search_keyword = ""           # 要搜索的关键字
    sheet_name = "主机"      # 查找的表

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
        skip_rows=skip_rows,
        format_column="主机编号", 
        uppercase=True,
        append_mode=False
    )

    # 根据需要改写
    for index, row in asset_data.iterrows():
        # 购入
        if WAY == PURCHASE:
             print(f"资产名称: {'主机'}, 资产编码: {str(row['主机编号'])}")
            #print(f"资产名称: {'显示器'}, 资产编码: {str(row['编号'])}")
            
        elif WAY == RENT:
             # 租赁
            print(f"资产名称: {row['资产名称']},  型号: {row['型号']},  租赁日期: {row['租赁日期']}, S/N号: {row['S/N号']}, 资产编号: {row['资产编号']}")
            
        elif WAY == DONATE:
            # 捐赠
            print(f"资产名称: {row['资产名称']},  型号: {row['型号']},  购入或入账日期: {row['登陆日期']}, S/N号: {ensure_string(row['S/N号'])}, 资产编号: {row['资产编号']}")
          
        


