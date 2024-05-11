import dash
from dash import dcc, html  # 更新导入语句
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

win_file = r'D:\1008\py_code\py\data\availability\\'  # 文件夹路径

# 加载 Excel 文件
file_path = win_file + "APISearch.xlsx"  # 更改为你的文件路径
data = pd.read_excel(file_path, sheet_name='priceAndInventory')

data['saleDate'] = pd.to_datetime(data['saleDate'])

# 计算所需数据
inventory_sum_daily = data.groupby('saleDate')['count'].sum().reset_index()
inventory_sum_by_hotel = data.groupby('hotelId')['count'].sum().reset_index().sort_values('count', ascending=False).head(10)
pivot_table = data.pivot_table(values='count', index='hotelId', columns='saleDate', fill_value=0)

# 创建应用
app = dash.Dash(__name__)

# 应用布局
app.layout = html.Div(children=[
    html.H1(children='Hotel Inventory Analysis'),

    html.Div([
        dcc.Graph(
            id='daily-total-inventory',
            figure=px.line(inventory_sum_daily, x='saleDate', y='count', title='Daily Total Inventory Across All Hotels',
                           labels={'count': 'Total Inventory', 'saleDate': 'Sale Date'})
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='top-hotels-by-inventory',
            figure=px.bar(inventory_sum_by_hotel, x='hotelId', y='count', title='Top 10 Hotels by Inventory',
                          labels={'count': 'Total Inventory', 'hotelId': 'Hotel ID'})
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='inventory-distribution',
            figure=px.box(data, x='saleDate', y='count', title='Distribution of Inventory by Date',
                          labels={'count': 'Inventory', 'saleDate': 'Sale Date'})
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='heatmap-inventory',
            figure=px.imshow(pivot_table, aspect='auto', color_continuous_scale='Viridis',
                             labels=dict(x='Sale Date', y='Hotel ID', color='Inventory'),
                             title='Heatmap of Inventory by Hotel and Date')
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='inventory-pie-chart',
            figure=px.pie(inventory_sum_by_hotel, values='count', names='hotelId', title='Inventory Proportion by Hotel')
        ),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)
