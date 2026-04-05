import pandas as pd
import time
import efinance as ef
import pandas as pd
import math

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import HoverTool

BASE = 'D:\Trae\bokeh\ai_team_collaboration\data'
klt = 101
display = 260
def plot_chart(klt, stock_id):
    filename = f'{BASE}/{klt}{stock_id}'
    data = ef.stock.get_quote_history(stock_id, klt=klt)
    # print(f'"One minute data:", {df.head(3)}')
    basic=data.iloc[-1,:2].to_dict()
    # print(f'basic: {basic}')
    print(basic['股票名称'])
    print(basic)
    # print(f'{basic[0]}+'/'+{basic[1]}')
    data.drop(data.columns[[0,1,8,9,10,11,12]], axis=1, inplace=True)
    data.rename(columns={'日期':'date', '收盘':'close', '开盘':'open', '最高':'high', '最低':'low', '成交量':'volume'}, inplace=True)

    # if klt == 101 or klt == 102 or klt == 103:
    #     df.set_index('date').astype(str)
    # elif klt == 1 or klt == 5 or klt == 15 or klt == 60:
    #     df.set_index('date').astype(str)

    print(data.tail(2))

    print(time.time() - start_time)
    
    df = data[-display:]
    
    # 读取合并分形数据
    try:
        fractal_df = pd.read_csv(stock_id + '_merged_fractals.csv', header=0, names=['index', 'date', 'open', 'close', 'high', 'low', 'volume', 'top', 'bottom', 'merged'])
        # 将top、bottom和merged列转换为布尔值
        fractal_df['top'] = fractal_df['top'].astype(bool)
        fractal_df['bottom'] = fractal_df['bottom'].astype(bool)
        fractal_df['merged'] = fractal_df['merged'].astype(bool)
        # 将日期列转换为datetime类型
        fractal_df['date'] = pd.to_datetime(fractal_df['date'])
        df['date'] = pd.to_datetime(df['date'])
        
        # 确保分形数据与K线数据日期范围一致
        fractal_df = fractal_df[fractal_df['date'].isin(df['date'])]
        
        # 获取分形数据
        top_fractals = fractal_df[fractal_df['top'] == True]
        bottom_fractals = fractal_df[fractal_df['bottom'] == True]
        print(f"读取到顶分形数量: {len(top_fractals)}")
        print(f"读取到底分形数量: {len(bottom_fractals)}")
        print(f"合并K线数量: {fractal_df['merged'].sum()}")
        print(f"顶分形数据:\n{top_fractals.head()}")
        print(f"底分形数据:\n{bottom_fractals.head()}")
        
        # 设置日期索引
        df.set_index('date', inplace=True)
        fractal_df.set_index('date', inplace=True)
        top_fractals.set_index('date', inplace=True)
        bottom_fractals.set_index('date', inplace=True)
        
        # 将分形数据合并到K线数据中
        df = df.join(fractal_df[['top', 'bottom', 'merged']])
        
        # 填充NaN值，确保所有K线都有merged列
        df['merged'] = df['merged'].fillna(False)
        df['top'] = df['top'].fillna(False)
        df['bottom'] = df['bottom'].fillna(False)
    except FileNotFoundError:
        print("未找到合并分形数据文件，将只显示K线图")
        top_fractals = pd.DataFrame()
        bottom_fractals = pd.DataFrame()
    except Exception as e:
        print(f"读取分形数据时出错: {e}")
        top_fractals = pd.DataFrame()
        bottom_fractals = pd.DataFrame()
    
    # 创建Bokeh图表 - 使用分类轴避免日期空白
    p = figure(title=f"{stock_id} K线图 - 顶底分形", x_axis_label='日期', y_axis_label='价格', 
               width=1200, height=600)
    
    # 重置索引以确保数据源正确
    df_reset = df.reset_index()
    
    # 添加HOVER工具显示日期
    hover = HoverTool(
        tooltips=[
            ("日期", "@date{%F %H:%M}"),
            ("开盘", "@open{0.00}"),
            ("最高", "@high{0.00}"),
            ("最低", "@low{0.00}"),
            ("收盘", "@close{0.00}"),
            ("成交量", "@volume{0,0}"),
            ("合并", "@merged")
        ],
        formatters={
            '@date': 'datetime'
        },
        mode='vline'
    )
    p.add_tools(hover)
    
    # 绘制K线蜡烛图 - 使用分类轴
    inc = df_reset.close > df_reset.open
    dec = df_reset.open > df_reset.close
    
    # 分离合并和非合并的K线
    merged_kline = df_reset[df_reset['merged'] == True]
    non_merged_kline = df_reset[df_reset['merged'] == False]
    
    # 绘制非合并K线（实心）
    p.segment('index', 'high', 'index', 'low', color="black", source=non_merged_kline)
    p.vbar(x='index', width=0.8, top='close', bottom='open', fill_color="#06982d", line_color="black", source=non_merged_kline[non_merged_kline['close'] > non_merged_kline['open']])
    p.vbar(x='index', width=0.8, top='open', bottom='close', fill_color="#ae1325", line_color="black", source=non_merged_kline[non_merged_kline['open'] > non_merged_kline['close']])
    
    # 绘制合并K线（空心，细黑边框）
    p.segment('index', 'high', 'index', 'low', color="black", source=merged_kline)
    p.vbar(x='index', width=0.8, top='close', bottom='open', fill_color="white", line_color="black", line_width=1, source=merged_kline[merged_kline['close'] > merged_kline['open']])
    p.vbar(x='index', width=0.8, top='open', bottom='close', fill_color="white", line_color="black", line_width=1, source=merged_kline[merged_kline['open'] > merged_kline['close']])
    
    # 添加顶底分形箭头标记
    if not top_fractals.empty:
        # 获取顶分形数据并匹配到K线数据索引
        top_fractals_reset = top_fractals.reset_index()
        # 找到顶分形在K线数据中的位置
        top_indices = []
        top_highs = []
        for _, row in top_fractals_reset.iterrows():
            match_idx = df_reset[df_reset['date'] == row['date']].index
            if len(match_idx) > 0:
                top_indices.append(match_idx[0])
                top_highs.append(row['high'])
        
        if top_indices:
            # 添加红色向下箭头表示顶分形（位于K线高点上方2%）
            arrow_offset = [h * 1.02 for h in top_highs]
            p.triangle(top_indices, arrow_offset, size=5, color='red', angle=math.pi, legend_label='顶分形')
        
    if not bottom_fractals.empty:
        # 获取底分形数据并匹配到K线数据索引
        bottom_fractals_reset = bottom_fractals.reset_index()
        # 找到底分形在K线数据中的位置
        bottom_indices = []
        bottom_lows = []
        for _, row in bottom_fractals_reset.iterrows():
            match_idx = df_reset[df_reset['date'] == row['date']].index
            if len(match_idx) > 0:
                bottom_indices.append(match_idx[0])
                bottom_lows.append(row['low'])
        
        if bottom_indices:
            # 添加绿色向上箭头表示底分形（位于K线低点下方2%）
            arrow_offset = [l * 0.98 for l in bottom_lows]
            p.triangle(bottom_indices, arrow_offset, size=5, color='green', angle=0, legend_label='底分形')

    output_file('custom_datetime_axis.html', title='custom_datetime_axis.py example')
    print(df.iloc[-1])

    # 设置x轴标签覆盖，避免周末和假期产生空白
    # 使用连续索引而不是日期索引来避免空白
    date_mapping = {}
    for i, date in enumerate(df_reset['date']):
        date_mapping[i] = date.strftime('%Y/%m/%d')
    p.xaxis.major_label_overrides = date_mapping
    
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    
    show(p)
    df.to_csv(stock_id)
klt = 101
stock_id = 'AAPL'
start_time = time.time()
plot_chart(klt, stock_id)
# df = pd.DataFrame(data)
print(f'处理时长：{time.time() - start_time}')