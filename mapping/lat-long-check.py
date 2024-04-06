
# 用经纬度确认两点距离py

import pandas as pd
import math
from tqdm import tqdm
import time

# 定义哈弗西公式计算两点间距离的函数，单位为米
def haversine(lat1, lon1, lat2, lon2):
    # 将十进制度数转化为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 哈弗西公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000 # 地球平均半径，单位为米
    return c * r

# 读取Excel文件
file_name = 'jtb-zyx-long-lat-check.xlsx'
df = pd.read_excel(file_name)

# 准备进度条
tqdm.pandas(desc="计算距离")

# 记录开始时间
start_time = time.time()

# 对每一行计算距离，并创建新列存储结果
df['distance_m'] = df.progress_apply(lambda row: haversine(row['z-lat'], row['z-long'], row['j-lat'], row['j-long']), axis=1)

# 计算所需时间
elapsed_time = time.time() - start_time
print(f"完成计算，耗时：{elapsed_time:.2f}秒")

# 将结果保存到CSV文件
output_file_name = 'updated_distances.csv'
df.to_csv(output_file_name, index=False)

print(f"结果已保存到 {output_file_name}")
