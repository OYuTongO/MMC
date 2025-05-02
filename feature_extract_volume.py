import pandas as pd
import os

# 指定要读取的文件目录
input_dir = './processed_data/volume_outlier_processed'  # 替换为你的输入文件目录

# 指定要保存结果的文件目录
output_dir = './extracted_features/volume_rate'  # 替换为你的输出文件目录

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)

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
        
        print(f"Processed {filename} and saved to {output_path}")