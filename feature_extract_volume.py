import pandas as pd
import os
import matplotlib.pyplot as plt

# 指定要读取的文件目录
input_dir = './processed_data/volume_outlier_processed'  # 替换为你的输入文件目录

# 指定要保存结果的文件目录
output_dir = './extracted_features/volume_rate'  # 替换为你的输出文件目录

# 指定要保存图表的文件目录
charts_dir = './extracted_features/volume_rate/charts'  # 替换为你的图表文件目录

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)
os.makedirs(charts_dir, exist_ok=True)

# 遍历输入目录中的所有文件
for filename in os.listdir(input_dir):
    if filename.endswith('.csv'):  # 假设文件是CSV格式
        # 构建完整的文件路径
        input_path = os.path.join(input_dir, filename)
        
        # 读取CSV文件
        df = pd.read_csv(input_path)
        
        # 转换时间格式
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # 提取成交量变化率特征
        df['volume_change_rate'] = df['volume'].pct_change()
        
        # 将结果保留三位小数
        df['volume_change_rate'] = df['volume_change_rate'].round(3)
        
        # 构建输出文件路径
        output_filename = f"feature_{filename}"
        output_path = os.path.join(output_dir, output_filename)
        
        # 保存结果到新的CSV文件
        df.to_csv(output_path, index=False)
        
        # 绘制成交量变化率图表
        plt.figure(figsize=(12, 6))
        plt.plot(df['datetime'], df['volume_change_rate'], label='Volume Change Rate')
        plt.title(f'Volume Change Rate for {filename}')
        plt.xlabel('Time')
        plt.ylabel('Volume Change Rate')
        plt.legend()
        plt.grid(True)
        
        # 构建图表文件路径
        chart_filename = f"chart_{filename}.png"
        chart_path = os.path.join(charts_dir, chart_filename)
        
        # 保存图表
        plt.savefig(chart_path)
        plt.close()
        
        print(f"Processed {filename} and saved to {output_path}")
        print(f"Saved chart to {chart_path}")