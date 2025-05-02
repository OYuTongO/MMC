import pandas as pd
import os
import glob
from datetime import datetime

def preprocess(data_folder, start_date=None, end_date=None, output_folder=None):
    """
    按照 symbol 合并所有主力合约数据，并清洗不匹配日期的数据，去除不需要的列
    
    参数:
    data_folder: 原始数据文件夹路径
    start_date: 起始日期 (YYYYMMDD)
    end_date: 结束日期 (YYYYMMDD)
    output_folder: 输出数据文件夹路径
    """
    file_pattern = os.path.join(data_folder, "*.csv.gz")
    all_files = sorted(glob.glob(file_pattern))

    # 过滤指定时间范围内的文件
    files_to_process = []
    for file_path in all_files:
        file_date = os.path.basename(file_path).split('.')[0]
        if (not start_date or file_date >= start_date) and \
           (not end_date or file_date <= end_date):
            files_to_process.append(file_path)

    symbol_data = {}

    for file_path in files_to_process:
        file_date_str = os.path.basename(file_path).split('.')[0]
        try:
            file_date = datetime.strptime(file_date_str, "%Y%m%d").date()
            df = pd.read_csv(file_path, compression='gzip')

            # 删除 exchange 列（如果存在）
            for col in ['exchange', 'symbol', 'contract']:
                if col in df.columns:
                    df.drop(col, axis=1, inplace=True)

            # 转换 datetime 列为 datetime 类型
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df[df['datetime'].dt.date == file_date]  # 删除日期不一致的行

            # 重新读取 symbol 和 contract 列用于主力合约判断
            raw_df = pd.read_csv(file_path, compression='gzip')
            raw_df['datetime'] = pd.to_datetime(raw_df['datetime'])
            raw_df = raw_df[raw_df['datetime'].dt.date == file_date]  # 同样清除不符行

            for symbol in raw_df['symbol'].unique():
                sym_data = raw_df[raw_df['symbol'] == symbol]
                contract_volume = sym_data.groupby('contract')['volume'].sum()
                main_contract = contract_volume.idxmax() if not contract_volume.empty else sym_data['contract'].value_counts().idxmax()
                sym_main_data = sym_data[sym_data['contract'] == main_contract]

                # 再次保留 datetime 并去掉多余列
                final_data = sym_main_data[['datetime', 'open', 'high', 'low', 'close', 'openinterest', 'volume', 'amount']]

                if symbol not in symbol_data:
                    symbol_data[symbol] = final_data
                else:
                    symbol_data[symbol] = pd.concat([symbol_data[symbol], final_data], ignore_index=True)

            print(f"✔ 已处理文件: {file_path}")
        except Exception as e:
            print(f"❌ 处理文件 {file_path} 时出错: {e}")

    # 输出到文件
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for symbol, df in symbol_data.items():
        df.to_csv(os.path.join(output_folder, f"{symbol}.csv"), index=False, encoding='utf-8-sig')
        print(f"✅ 已保存文件: {symbol}.csv，共 {len(df)} 行")

# 使用示例
if __name__ == "__main__":
    preprocess(
        data_folder="./raw_data",
        start_date="20170101",
        end_date="20250418",
        output_folder="./preprocessed_data"
    )
