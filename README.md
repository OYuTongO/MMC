# 预处理
1.运行Preprocess.py得到pre_1_data保存异常值处理前的数据&得到pre_2_data保存异常值处理后的数据
2.运行v0.py得到异常值处理前的
3.运行v1.py得到异常值处理前的close概率密度函数,v2.py得到异常值处理后的close数值k线图
4.运行OutlierClean.py得到volume的前后对比可视化图片(保存在文件夹v3),数据的进一步清洗最终存放在pre_3_data目录下

# 特征提取
1.运行VolumeRate.py得到包含交易量变化率这一特征,保存在feature_1文件夹,可视化在visualize_1文件夹
2.运行LagFeature.py得到交易量volume滞后30分钟和滞后1天的特征,保存在feature_2文件夹
3.运行CrossFeature.py得到交叉特征(波动率*交易量)

# 模型的训练与验证

# 模型的效果

# 模型的改进建议