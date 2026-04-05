import numpy as np
import pandas as pd
import os

def merge_kline(df):
    """
    缠论方向性合并算法
    包含正向（从过去到现在）和反向（从现在到过去）两个阶段
    """
    # 复制数据避免修改原始数据
    df_merged = df.copy()
    df_merged['merged'] = False
    
    # 获取高点和低点数组
    dfh = df_merged['high'].values
    dfl = df_merged['low'].values
    
    print(f"开始正向合并处理，共 {len(df_merged)} 根K线")
    
    # 第一阶段：从过去到现在处理K线包含关系
    i = 0
    long_candle = 0
    
    while i < len(df_merged) - 1:
        # 查找包含关系
        if dfh[long_candle] >= dfh[i + 1] and dfl[long_candle] <= dfl[i + 1]:   # 左包含右
            # 被包含的K线在i + 1
            df_merged.iloc[i + 1, df_merged.columns.get_loc('merged')] = True
            # 长K线在原位不改变
            # long_candle = i
            print(f"正向合并：K线 {i +1} 被 K线 {long_candle} 包含")
            i += 1
            
        # 如果没有包含关系，向右移动
        else:
            i += 1
            long_candle = i
    
    print(f"开始反向合并处理")
    
    # 第二阶段：从现在到过去处理K线包含关系
    i = len(df_merged) - 1
    long_candle = len(df_merged) - 1
    
    while i > 0:
        # 查找包含关系
        if dfh[long_candle] >= dfh[i - 1] and dfl[long_candle] <= dfl[i - 1]:   # 右包含左（当前K线包含前一根K线）
            # 被包含的K线在i - 1
            df_merged.iloc[i - 1, df_merged.columns.get_loc('merged')] = True
            # 长K线在原位不改变
            # long_candle = i
            print(f"反向合并：K线 {i - 1} 被 K线 {long_candle} 包含, 右包左")
            i -= 1
     
        # 如果没有包含关系，向左移动
        else:
            print(f"反向合并：K线{i}与K线{i -1}没有包含关系，向左移动继续合并")
            i -= 1
            long_candle = i
            
    return df_merged

def identify_fractals_alternating(df):
    """
    交替识别顶底分形
    第一个分形确定后，必须执行交替找下个分形

    Args:
        df: K线数据DataFrame
        
    Returns:
        fractal_df: 包含分形标记的DataFrame
    """
    data = df.copy()
    
    # 初始化分形列
    data['top'] = False
    data['bottom'] = False
    
    # 至少需要5根K线才能判断分形
    if len(data) < 5:
        return data
    
    # 找到第一个分形
    first_fractal_type = None
    first_fractal_index = -1
    
    for i in range(2, len(data) - 2):
        current = data.iloc[i]
        prev2 = data.iloc[i-2]
        prev1 = data.iloc[i-1]
        next1 = data.iloc[i+1]
        next2 = data.iloc[i+2]
        
        # 检查顶分形
        top_conditions = [
            current['high'] > prev2['high'],
            current['high'] > prev1['high'],
            current['high'] > prev1['close'],
            current['high'] > next1['high'],
            current['high'] > next2['high'],
            current['high'] > next1['close']
        ]
        
        # 检查底分形
        bottom_conditions = [
            current['low'] < prev2['low'],
            current['low'] < prev1['low'],
            current['low'] < next1['low'],
            current['low'] < next2['low']
        ]
        
        # 临时改变sum(top_conditions) == 6:，原来：sum(top_conditions) >= 3:
        if sum(top_conditions) == 6:
            first_fractal_type = 'top'
            first_fractal_index = i
            data.loc[data.index[i], 'top'] = True
            break
        elif sum(bottom_conditions) >= 3:
            first_fractal_type = 'bottom'
            first_fractal_index = i
            data.loc[data.index[i], 'bottom'] = True
            break
    
    # 如果找到第一个分形，继续交替寻找
    if first_fractal_type:
        current_type = 'bottom' if first_fractal_type == 'top' else 'top'
        start_index = first_fractal_index + 1
        
        for i in range(start_index, len(data) - 2):
            current = data.iloc[i]
            prev2 = data.iloc[i-2]
            prev1 = data.iloc[i-1]
            next1 = data.iloc[i+1]
            next2 = data.iloc[i+2]
            
            if current_type == 'top':
                # 寻找顶分形
                conditions = [
                    current['high'] > prev2['high'],
                    current['high'] > prev1['high'],
                    current['high'] > next1['high'],
                    current['high'] > next2['high']
                ]
                # 源码sum(conditions) >= 3:
                if sum(conditions) == 6:
                    data.loc[data.index[i], 'top'] = True
                    current_type = 'bottom'  # 下一个找底分形
            else:
                # 寻找底分形
                conditions = [
                    current['low'] < prev2['low'],
                    current['low'] < prev1['low'],
                    current['low'] < next1['low'],
                    current['low'] < next2['low']
                ]
                if sum(conditions) >= 3:
                    data.loc[data.index[i], 'bottom'] = True
                    current_type = 'top'  # 下一个找顶分形
    
    return data

def _get_valid_kline(data, start_index, direction):
    """
    获取有效的K线数据，跳过合并的K线
    
    Args:
        data: K线数据DataFrame
        start_index: 起始索引
        direction: 搜索方向 (-1: 向前, 1: 向后)
        
    Returns:
        kline: 有效的K线数据，如果找不到则返回None
    """
    index = start_index
    max_steps = 10  # 最多搜索10步
    steps = 0
    
    while 0 <= index < len(data) and steps < max_steps:
        kline = data.iloc[index]
        if not kline.get('merged', False):
            # 返回单个值的字典而不是Series
            return {
                'high': kline['high'],
                'low': kline['low']
            }
        index += direction
        steps += 1
    
    return None


def identify_fractals_alternating_with_bypass(df):
    """
    交替识别顶底分形，如果merged==True则跳过该K线
    第一个分形确定后，必须执行交替找下个分形

    Args:
        df: K线数据DataFrame
        
    Returns:
        fractal_df: 包含分形标记的DataFrame
    """
    data = df.copy()
    
    # 初始化分形列
    data['top'] = False
    data['bottom'] = False
    
    # 至少需要5根K线才能判断分形
    if len(data) < 5:
        return data
    
    # 找到第一个分形
    first_fractal_type = None
    first_fractal_index = -1
    
    for i in range(2, len(data) - 2):
        current = data.iloc[i]
        
        # 如果当前K线被合并，跳过
        if current.get('merged', False):
            continue
            
        # 获取前后K线，跳过合并的K线
        prev2 = _get_valid_kline(data, i-2, -1)
        prev1 = _get_valid_kline(data, i-1, -1)
        next1 = _get_valid_kline(data, i+1, 1)
        next2 = _get_valid_kline(data, i+2, 1)
        
        # 如果无法找到足够数量的有效K线，跳过
        if None in [prev2, prev1, next1, next2]:
            continue
        
        # 检查顶分形
        top_conditions = [
            current['high'] > prev2['high'],
            current['high'] > prev1['high'],
            current['high'] > next1['high'],
            current['high'] > next2['high']
        ]
        
        # 检查底分形
        bottom_conditions = [
            current['low'] < prev2['low'],
            current['low'] < prev1['low'],
            current['low'] < next1['low'],
            current['low'] < next2['low']
        ]
        
        # 修改条件：顶分形需要至少3个条件满足，底分形需要至少3个条件满足
        if sum(top_conditions) >= 3:
            first_fractal_type = 'top'
            first_fractal_index = i
            data.loc[data.index[i], 'top'] = True
            break
        elif sum(bottom_conditions) >= 3:
            first_fractal_type = 'bottom'
            first_fractal_index = i
            data.loc[data.index[i], 'bottom'] = True
            break
    
    # 如果找到第一个分形，继续交替寻找
    if first_fractal_type:
        current_type = 'bottom' if first_fractal_type == 'top' else 'top'
        start_index = first_fractal_index + 1
        
        for i in range(start_index, len(data) - 2):
            current = data.iloc[i]
            
            # 如果当前K线被合并，跳过
            if current.get('merged', False):
                continue
                
            # 获取前后K线，跳过合并的K线
            prev2 = _get_valid_kline(data, i-2, -1)
            prev1 = _get_valid_kline(data, i-1, -1)
            next1 = _get_valid_kline(data, i+1, 1)
            next2 = _get_valid_kline(data, i+2, 1)
            
            # 如果无法找到足够数量的有效K线，跳过
            if None in [prev2, prev1, next1, next2]:
                continue
                
            if current_type == 'top':
                # 寻找顶分形
                conditions = [
                    current['high'] >= prev2['high'],
                    current['high'] >= prev1['high'],
                    current['high'] >= next1['high'],
                    current['high'] >= next2['high']
                ]
                # 修改条件：顶分形需要至少3个条件满足
                if sum(conditions) >= 3:
                    # 后向验证：检查后一根K线的高点是否高于当前顶分形的顶
                    next_kline = _get_valid_kline(data, i+1, 1)
                    if next_kline and next_kline['high'] > current['high']:
                        # 向后移动顶分形一位
                        data.loc[data.index[i], 'top'] = False
                        data.loc[data.index[i+1], 'top'] = True
                        current_type = 'bottom'  # 下一个找底分形
                    else:
                        data.loc[data.index[i], 'top'] = True
                        current_type = 'bottom'  # 下一个找底分形
            else:
                # 寻找底分形
                conditions = [
                    current['low'] <= prev2['low'],
                    current['low'] <= prev1['low'],
                    current['low'] <= next1['low'],
                    current['low'] <= next2['low']
                ]
                if sum(conditions) >= 3:
                    # 后向验证：检查后一根K线的低点是否低于当前底分形的底
                    next_kline = _get_valid_kline(data, i+1, 1)
                    if next_kline and next_kline['low'] < current['low']:
                        # 向后移动底分形一位
                        data.loc[data.index[i], 'bottom'] = False
                        data.loc[data.index[i+1], 'bottom'] = True
                        current_type = 'top'  # 下一个找顶分形
                    else:
                        data.loc[data.index[i], 'bottom'] = True
                        current_type = 'top'  # 下一个找顶分形
    
    return data

def main():
    # 读取AAPL.csv数据
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, 'AAPL.csv')
    df = pd.read_csv(input_path, header=0, index_col=0)
    # 重置索引，确保index列存在
    df = df.reset_index()
    # 重命名列，确保列名正确
    df.columns = ['index', 'date', 'open', 'close', 'high', 'low', 'volume']
    
    # 添加三列到原始数据集
    df['top'] = False
    df['bottom'] = False
    df['merged'] = False
    
    # 不再拷贝AAPL.csv，直接使用分形数据
    
    # 执行K线合并
    print("开始K线合并...")
    merged_df = merge_kline(df)
    print(f"原始数据行数: {len(df)}")
    print(f"合并后数据行数: {len(merged_df)}")
    
    # 将合并信息映射回原始数据
    # 直接从合并后的DataFrame获取merged标记
    df['merged'] = merged_df['merged']
    
    merged_count = df['merged'].sum()
    print(f"被合并的K线数量: {merged_count}")
    merged_indices = df[df['merged']]['index'].tolist()
    print(f"被合并的K线索引示例: {merged_indices[:10] if merged_indices else '无'}")
    
    # 在原始数据上识别分形 - 使用带bypass的交替分形检测
    print("开始在原始数据上交替识别分形(跳过合并K线)...")
    fractal_df = identify_fractals_alternating_with_bypass(df)
    
    # 统计分形数量
    top_count = fractal_df['top'].sum()
    bottom_count = fractal_df['bottom'].sum()
    print(f"识别到顶分形数量: {top_count}")
    print(f"识别到底分形数量: {bottom_count}")
    
    # 保存结果到本地脚本目录
    output_file = 'AAPL_merged_fractals.csv'
    output_path = os.path.join(script_dir, output_file)
    
    fractal_df.to_csv(output_path, index=False, header=True)
    print(f"合并分形数据已保存到: {output_path}")
    print(f"保存的列: {list(fractal_df.columns)}")
    
    # 显示前几行数据
    print("\n合并后数据前10行:")
    print(fractal_df.head(10))

if __name__ == "__main__":
    main()

