import pandas as pd

def compare_tables_and_find_missing(table1_path, table2_path, key_columns, 
                           sheet1_name=0, sheet2_name=0,
                           output_file='missing_records.xlsx',
                           columns_to_upper=None,
                           show_all_columns=True):
    """
    比较两个非对齐、乱序的Excel表格，找出第二张表中缺少的记录
    
    参数:
        table1_path: 基准表路径
        table2_path: 对比表路径
        key_columns: 关键字段(单个列名或列名列表)
        sheet1_name: 表1的工作表名/索引
        sheet2_name: 表2的工作表名/索引
        output_file: 输出文件路径
        columns_to_upper: 需要转为大写的列(单个或列表)
        show_all_columns: 是否在结果中显示所有列(True)或仅显示关键列(False)
    
    返回:
        返回缺少记录的DataFrame
    """
    try:
        # 读取数据
        df1 = pd.read_excel(table1_path, sheet_name=sheet1_name)
        df2 = pd.read_excel(table2_path, sheet_name=sheet2_name)
        
        print(f"基准表记录数: {len(df1)} | 对比表记录数: {len(df2)}")
        
        # 统一关键字段格式
        if isinstance(key_columns, str):
            key_columns = [key_columns]
        
        # 检查关键字段是否存在
        missing_cols1 = [col for col in key_columns if col not in df1.columns]
        missing_cols2 = [col for col in key_columns if col not in df2.columns]
        
        if missing_cols1:
            raise ValueError(f"表1中缺少关键字段: {missing_cols1}")
        if missing_cols2:
            raise ValueError(f"表2中缺少关键字段: {missing_cols2}")
        
        # 处理大小写转换
        if columns_to_upper:
            columns_to_upper = [columns_to_upper] if isinstance(columns_to_upper, str) else columns_to_upper
            
            for df in [df1, df2]:
                for col in columns_to_upper:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.upper()
                        print(f"列 '{col}' 已转为大写")
        
        # 为两个表创建合并关键字段
        for df in [df1, df2]:
            df['_merge_key'] = df[key_columns].astype(str).apply(lambda x: '|'.join(x), axis=1)
        
        # 找出表1有但表2没有的记录
        missing_keys = set(df1['_merge_key']) - set(df2['_merge_key'])
        missing_records = df1[df1['_merge_key'].isin(missing_keys)]
        
        # 清理临时列
        for df in [df1, df2, missing_records]:
            if '_merge_key' in df.columns:
                df.drop('_merge_key', axis=1, inplace=True)
        
        # 处理输出列
        if not show_all_columns and len(missing_records) > 0:
            missing_records = missing_records[key_columns + [c for c in missing_records.columns if c not in key_columns and c not in columns_to_upper]]
        
        print(f"\n发现 {len(missing_records)} 条缺失记录")
        
        # 保存结果
        if len(missing_records) > 0:
            missing_records.to_excel(output_file, index=False)
            print(f"结果已保存至: {output_file}")
            print("\n缺失记录示例:")
            print(missing_records.head())
        else:
            print("两张表的关键字段完全匹配，无缺失记录")
        
        return missing_records
    
    except Exception as e:
        print(f"错误发生: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    # 示例参数 - 请根据实际情况修改
    table1_path = "/home/ubuntu/Downloads/zj_info1.xlsx"      # 第一张表路径
    table2_path = "/home/ubuntu/Downloads/zj_info2.xlsx"      # 第二张表路径
    key_columns = ["assetCode"]  # 用于比较的关键字段(可以是一个或多个)
    output_file = "/home/ubuntu/Downloads/compire_outcome_zj.xlsx"  # 输出文件路径
    
    # 调用函数
    result = compare_tables_and_find_missing(
        table1_path=table1_path,
        table2_path=table2_path,
        key_columns=key_columns,
        output_file=output_file
    )
    
    if result is not None and len(result) > 0:
        print("\n缺少的记录预览:")
        print(result.head())