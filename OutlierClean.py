"""
VolumeOutlierCleaner
-------------------
专门用于股票交易量(volume)数据的异常值检测与处理工具
简化版：仅处理volume列，优化代码结构
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 设置中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def detect_and_handle_volume_outliers(df, lower_multiplier=1.2, upper_multiplier=25):
    """
    检测并处理交易量(volume)异常值
    
    参数:
    df: 包含volume列的DataFrame
    lower_multiplier: 下界计算乘数，默认1.2
    upper_multiplier: 上界计算乘数，默认25
    
    返回:
    处理后的DataFrame和统计信息
    """
    column = 'volume'  # 固定处理交易量列
    result_df = df.copy()
    
    # 计算IQR统计量
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    
    # 计算异常值边界
    lower_bound = q1 - lower_multiplier * iqr
    upper_bound = q3 + upper_multiplier * iqr
    
    # 确保下界不为负值
    lower_bound = max(0, lower_bound)
    
    # 标记异常值
    outliers_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    outliers_count = outliers_mask.sum()
    
    # 统计信息
    stats = {
        'q1': q1, 'q3': q3, 'iqr': iqr,
        'lower_bound': lower_bound, 'upper_bound': upper_bound,
        'outliers_count': outliers_count,
        'outliers_mask': outliers_mask
    }
    
    # 处理异常值
    if outliers_count > 0:
        # 保存原始值以便对比
        result_df[f'original_{column}'] = df[column].copy()
        
        # 将异常值替换为NaN
        result_df.loc[outliers_mask, column] = np.nan
        
        # 使用线性插值填充
        result_df[column] = result_df[column].interpolate(method='linear')
        # 处理边缘点
        result_df[column] = result_df[column].bfill().ffill()
    
    return result_df, stats


def visualize_volume_correction(sym, df, processed_df, outliers_mask, stats, sample_size=10000):
    """生成交易量异常值处理前后的对比可视化"""
    column = 'volume'  # 固定处理交易量列
    
    # 对大数据集进行采样
    if len(df) > sample_size:
        # 智能采样：保留所有异常值点和部分正常点
        all_indices = np.arange(len(df))
        outlier_positions = np.where(outliers_mask)[0]
        
        # 优先保留异常值点
        if len(outlier_positions) > 1000:
            sampled_outliers = np.random.choice(outlier_positions, size=1000, replace=False)
        else:
            sampled_outliers = outlier_positions
            
        # 再加入一些正常点
        non_outlier_positions = np.setdiff1d(all_indices, outlier_positions)
        remaining_slots = sample_size - len(sampled_outliers)
        
        if remaining_slots > 0 and len(non_outlier_positions) > remaining_slots:
            sampled_non_outliers = np.random.choice(
                non_outlier_positions, size=remaining_slots, replace=False)
            sample_indices = np.concatenate([sampled_outliers, sampled_non_outliers])
            sample_indices.sort()
        else:
            sample_indices = np.concatenate([sampled_outliers, non_outlier_positions])
            if len(sample_indices) > sample_size:
                sample_indices = np.random.choice(sample_indices, size=sample_size, replace=False)
                sample_indices.sort()
        
        # 创建采样数据
        sampled_orig_df = df.iloc[sample_indices].copy()
        sampled_proc_df = processed_df.iloc[sample_indices].copy()
        sampled_mask = outliers_mask.iloc[sample_indices].copy()
    else:
        sampled_orig_df = df
        sampled_proc_df = processed_df
        sampled_mask = outliers_mask
    
    # 创建双子图
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # 计算统一的y轴范围
    all_values = np.concatenate([
        sampled_orig_df[column].values,
        sampled_proc_df[column].values
    ])
    y_min = max(0, np.min(all_values) * 0.95)  # 确保不为负
    y_max = np.max(all_values) * 1.05
    
    # 子图1：原始数据和异常值标记
    axes[0].plot(sampled_orig_df.index, sampled_orig_df[column], 
             'b-', label=f'原始交易量', linewidth=1)
    
    # 标记异常值点
    outlier_points = sampled_orig_df[sampled_mask]
    if not outlier_points.empty:
        axes[0].scatter(
            outlier_points.index,
            outlier_points[column],
            color='red', s=10, label='检测到的异常值', alpha=0.8
        )
    
    # 绘制上下界限
    axes[0].axhline(y=stats['upper_bound'], color='r', linestyle='--', alpha=0.5, label='上界')
    axes[0].axhline(y=stats['lower_bound'], color='r', linestyle='--', alpha=0.5, label='下界')
    
    axes[0].set_ylim(y_min, y_max)
    axes[0].set_title(f'{sym} 交易量异常值检测前 (显示{len(sampled_orig_df)}个数据点)')
    axes[0].set_ylabel('交易量')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 子图2：处理后的数据
    axes[1].plot(sampled_proc_df.index, sampled_proc_df[column], 
             'g-', label=f'处理后交易量', linewidth=1)
    
    axes[1].set_ylim(y_min, y_max)
    axes[1].set_title(f'{sym} 交易量异常值处理后')
    axes[1].set_xlabel('日期时间')
    axes[1].set_ylabel('交易量')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def process_volume_outliers(data_dir='./processed_data/', symbols=None):
    """处理多个股票数据文件的交易量异常值"""
    # 确保输出目录存在
    output_dir = Path(data_dir) / 'volume_outlier_processed'
    output_dir.mkdir(exist_ok=True)
    
    # 创建图表输出目录
    plot_dir = output_dir / 'plots'
    plot_dir.mkdir(exist_ok=True)
    
    results = {}
    
    # 获取要处理的文件
    if symbols is None:
        file_pattern = '*.csv'
        all_files = list(Path(data_dir).glob(file_pattern))
        symbols = [f.stem.split('_')[0] for f in all_files]
    else:
        all_files = [Path(data_dir) / f"{sym}_data.csv" for sym in symbols]
    
    for sym, file_path in zip(symbols, all_files):
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            continue
            
        print(f"处理 {sym} 的交易量数据...")
        
        # 读取CSV文件
        try:
            df = pd.read_csv(file_path)
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            continue
            
        # 确认交易量列存在
        if 'volume' not in df.columns:
            print(f"volume列在{sym}数据中不存在，跳过")
            continue
            
        # 处理交易量异常值
        processed_df, stats = detect_and_handle_volume_outliers(
            df, lower_multiplier=1.2, upper_multiplier=25
        )
        
        # 输出处理结果
        print(f"  检测到的异常值数量: {stats['outliers_count']}")
        print(f"  IQR: {stats['iqr']:.2f}")
        print(f"  下界/上界: [{stats['lower_bound']:.2f}, {stats['upper_bound']:.2f}]")
        
        # 生成可视化和保存结果
        if stats['outliers_count'] > 0:
            # 创建可视化
            fig = visualize_volume_correction(
                sym, df, processed_df, stats['outliers_mask'], stats
            )
            
            # 保存图表
            plot_path = plot_dir / f"{sym}_volume_outliers.png"
            fig.savefig(plot_path)
            plt.close(fig)
            print(f"  可视化已保存至: {plot_path}")
            
            # 保存处理后的数据
            output_path = output_dir / f"{sym}_volume_processed.csv"
            processed_df.to_csv(output_path)
            print(f"  处理后的数据已保存至: {output_path}")
        
        # 保存处理结果
        results[sym] = {
            'stats': stats,
            'processed_data': processed_df
        }
    
    return results


if __name__ == "__main__":
    # 指定要处理的股票代码
    symbols_to_process = ['HC', 'SS', 'I', 'JM', 'RB', 'SF', 'SM']  # 可根据需要修改
    
    # 执行处理
    results = process_volume_outliers(
        data_dir='./processed_data/',
        symbols=symbols_to_process
    )
    
    # 输出汇总
    print("\n处理汇总:")
    for sym, result in results.items():
        stats = result['stats']
        print(f"\n{sym}:")
        print(f"  交易量异常值: {stats['outliers_count']} 个")
        if stats['outliers_count'] > 0:
            print(f"  IQR范围: [{stats['q1']:.2f}, {stats['q3']:.2f}], IQR: {stats['iqr']:.2f}")
            print(f"  异常值界限: [{stats['lower_bound']:.2f}, {stats['upper_bound']:.2f}]")