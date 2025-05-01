import pandas as pd
import glob
import os

def read_gz_csv_files(data_folder, start_date=None, end_date=None):
    """读取指定文件夹中的.csv.gz文件并合并为一个DataFrame"""
    
    # 获取所有匹配的文件
    file_pattern = os.path.join(data_folder, "*.csv.gz")
    all_files = sorted(glob.glob(file_pattern))
    
    # 根据日期范围过滤文件
    if start_date or end_date:
        filtered_files = []
        for file_path in all_files:
            file_date = os.path.basename(file_path).split('.')[0]
            if (not start_date or file_date >= start_date) and \
               (not end_date or file_date <= end_date):
                filtered_files.append(file_path)
        files_to_process = filtered_files
    else:
        files_to_process = all_files
    
    # 读取并合并所有文件
    dataframes = []
    for file_path in files_to_process:
        file_date = os.path.basename(file_path).split('.')[0]
        print(f"读取文件: {file_path}")
        
        df = pd.read_csv(file_path, compression='gzip')
        dataframes.append(df)
        # 删除交换所信息
        df = df.drop('exchange', axis=1, inplace=True)
    
    # 合并所有数据
    if dataframes:
        combined_data = pd.concat(dataframes, ignore_index=True)
        return combined_data
    else:
        return pd.DataFrame()

data = read_gz_csv_files(".\cta_data\cta_data\data", "20170101", "20250418")
print(f"读取了 {len(data)} 行数据")
# 将data的样式输出到指定文件
data.to_csv("output.csv", index=False, encoding='utf-8-sig')
print(data)