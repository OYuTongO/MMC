import pandas as pd
import os
import glob
from datetime import datetime

def process_futures_data(data_folder, symbol=None, start_date=None, end_date=None, output_folder=None, output_all=False):
    """
    处理期货数据，可指定期货品种，并删除非当天主力合约数据
    
    参数:
    data_folder: 数据文件夹路径
    symbol: 期货品种代码，如'HC'、'SS'等，不指定则处理所有品种
    start_date: 开始日期，格式为"YYYYMMDD"
    end_date: 结束日期，格式为"YYYYMMDD"
    output_folder: 输出文件夹，不指定则不保存文件
    output_all: 是否输出所有品种合并的数据文件，默认为False
    
    返回:
    处理后的DataFrame字典，键为品种代码，值为相应的DataFrame
    """
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
    
    # 创建字典用于存储每个品种的处理后数据
    processed_data_dict = {}
    
    # 逐个读取并处理文件
    for file_path in files_to_process:
        file_date = os.path.basename(file_path).split('.')[0]
        print(f"处理文件: {file_path}")
        
        try:
            # 读取数据
            df = pd.read_csv(file_path, compression='gzip')
            
            # 删除交换所信息（如果存在）
            if 'exchange' in df.columns:
                df.drop('exchange', axis=1, inplace=True)
            
            # 转换datetime列为datetime类型
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            # 提取日期部分
            df['date'] = df['datetime'].dt.date
            
            # 提取当天日期（从文件名中获取）
            current_date = datetime.strptime(file_date, "%Y%m%d").date()
            
            # 只保留当天的数据
            df = df[df['date'] == current_date]
            
            # 如果指定了品种，则只保留该品种的数据
            if symbol:
                df = df[df['symbol'] == symbol]
                
                # 如果过滤后没有数据，则跳过该文件
                if df.empty:
                    print(f"文件 {file_path} 中没有品种 {symbol} 的数据")
                    continue
            
            # 获取当前数据中的所有品种
            symbols = df['symbol'].unique()
            
            for sym in symbols:
                # 获取当前品种的数据
                sym_data = df[df['symbol'] == sym]
                
                # 确定当前品种的主力合约（基于交易量）
                contract_volume = sym_data.groupby('contract')['volume'].sum()
                
                # 如果没有交易量数据，则使用出现频率
                if contract_volume.empty:
                    contract_counts = sym_data['contract'].value_counts()
                    main_contract = contract_counts.index[0]
                else:
                    main_contract = contract_volume.idxmax()
                
                print(f"日期: {current_date}, 品种: {sym}, 主力合约: {main_contract}")
                
                # 只保留主力合约的数据
                sym_data = sym_data[sym_data['contract'] == main_contract]
                
                # 删除辅助列
                if 'date' in sym_data.columns:
                    sym_data.drop('date', axis=1, inplace=True)
                
                # 将处理后的数据添加到对应品种的DataFrame中
                if sym not in processed_data_dict:
                    processed_data_dict[sym] = sym_data
                else:
                    processed_data_dict[sym] = pd.concat([processed_data_dict[sym], sym_data], ignore_index=True)
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
    
    # 如果指定了输出文件夹，则保存处理后的数据
    if output_folder:
        # 确保输出文件夹存在
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # 保存每个品种的数据到单独的文件
        for sym, data in processed_data_dict.items():
            if not data.empty:
                output_file = os.path.join(output_folder, f"{sym}_futures_data.csv")
                data.to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"品种 {sym} 数据处理完成，共 {len(data)} 行，已保存到 {output_file}")
        
        # 如果需要，保存所有品种的合并数据
        if output_all and len(processed_data_dict) > 0:
            all_data = pd.concat(list(processed_data_dict.values()), ignore_index=True)
            all_output_file = os.path.join(output_folder, "all_futures_data.csv")
            all_data.to_csv(all_output_file, index=False, encoding='utf-8-sig')
            print(f"所有品种数据处理完成，共 {len(all_data)} 行，已保存到 {all_output_file}")
    
    return processed_data_dict

# 使用示例
if __name__ == "__main__":
    # 处理单个品种的示例
    hc_data_dict = process_futures_data(
        "./cta_data/cta_data/data",
        symbol="HC",
        start_date="20170101",
        end_date="20250418",
        output_folder="./processed_data"
    )
    
    # 处理所有品种并分别保存的示例
    all_data_dict = process_futures_data(
        "./cta_data/cta_data/data",
        start_date="20170101",
        end_date="20250418",
        output_folder="./processed_data",
        output_all=True  # 同时输出所有品种合并的数据
    )
    
    # 查看处理了哪些品种
    print(f"处理了以下品种: {list(all_data_dict.keys())}")
    
    # 统计每个品种的数据量
    for sym, data in all_data_dict.items():
        print(f"品种 {sym} 的数据量: {len(data)} 行")