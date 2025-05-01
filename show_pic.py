import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

# 设置文件夹路径
folder_path = "./processed_data"
output_folder = "./visualize"

# 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历文件夹中的所有CSV文件
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        # 构造完整的文件路径
        file_path = os.path.join(folder_path, filename)
        
        # 读取CSV文件
        df = pd.read_csv(file_path, parse_dates=['datetime'])
        
        # 设置图形风格
        plt.style.use('seaborn-v0_8-dark-palette')
        
        # 创建一个图形
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # 提取合约代码
        symbol_code = df['symbol'].iloc[0]
        
        # 绘制价格数据（开放价、最高价、最低价、收盘价）
        # ax1.plot(df['datetime'], df['open'], label='Open', color='blue')
        # ax1.plot(df['datetime'], df['high'], label='High', color='green')
        # ax1.plot(df['datetime'], df['low'], label='Low', color='red')
        ax1.plot(df['datetime'], df['close'], label='Close', color='orange')
        
        # 设置左轴的标签和标题
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Price')
        ax1.set_title(f'{symbol_code} Price and Volume')
        
        # 创建第二个y轴用于绘制交易量
        ax2 = ax1.twinx()
        ax2.bar(df['datetime'], df['volume'], color='purple', alpha=0.3, label='Volume')
        
        # 设置右轴的标签
        ax2.set_ylabel('Volume')
        
        # 合并图例
        fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.95))
        
        # 自动调整日期标签
        plt.gcf().autofmt_xdate()
        
        # 构造输出图像文件路径
        output_path = os.path.join(output_folder, f"{filename[:-4]}.png")
        
        # 保存图形到本地
        plt.savefig(output_path)
        
        # 关闭当前图形以释放内存
        plt.close()