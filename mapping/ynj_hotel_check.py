import pandas as pd
import math
from tqdm import tqdm
import time
from fuzzywuzzy import fuzz
import re  # 导入正则表达式库

# 定义字符串预处理函数
def preprocess_string(s):
    # 去除所有符号，只保留字母、数字和空格
    s = re.sub(r'[^\w\s]', '', s)
    # 去除前后空格
    s = s.strip()
    # 将双空格替换为单空格
    s = re.sub(r'\s+', ' ', s)
    # 可选：对单词进行排序（如果需要根据单词部分顺序比较）
    # s = ' '.join(sorted(s.split()))
    return s

# 更新相似度计算函数以使用预处理字符串
def name_similarity(name1, name2):
    preprocessed_name1 = preprocess_string(name1)
    preprocessed_name2 = preprocess_string(name2)
    return fuzz.ratio(preprocessed_name1, preprocessed_name2)

def address_similarity(address1, address2):
    preprocessed_address1 = preprocess_string(address1)
    preprocessed_address2 = preprocess_string(address2)
    return fuzz.ratio(preprocessed_address1, preprocessed_address2)
    
    
# 定义哈弗西公式计算两点间距离的函数，单位为米
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # 地球平均半径，单位为米
    return c * r

# 检查邮编是否一致
def check_zipcode(zip1, zip2):
    return zip1 == zip2

# 计算名称相似度
def name_similarity(name1, name2):
    return fuzz.ratio(name1, name2)

# 计算地址相似度
def address_similarity(address1, address2):
    return fuzz.ratio(address1, address2)

# 读取Excel文件
file_name = 'zyx_kr4731.xlsx'
df = pd.read_excel(file_name)

# 准备进度条
tqdm.pandas(desc="处理数据")

# 记录开始时间
start_time = time.time()

# 对每一行应用函数，并创建新列存储结果
df['distance_m'] = df.progress_apply(lambda row: haversine(row['z-lat'], row['z-long'], row['j-lat'], row['j-long']), axis=1)
df['zipcode_same'] = df.progress_apply(lambda row: check_zipcode(row['z-zipcode'], row['j-zipcode']), axis=1)
df['name_similarity'] = df.progress_apply(lambda row: name_similarity(row['z-name'], row['j-name']), axis=1)
df['address_similarity'] = df.progress_apply(lambda row: address_similarity(row['z-address'], row['j-address']), axis=1)

# 计算所需时间
elapsed_time = time.time() - start_time
print(f"完成计算，耗时：{elapsed_time:.2f}秒")

# 将结果保存到CSV文件
output_file_name = 'updated_distances.csv'
df.to_csv(output_file_name, index=False)

print(f"结果已保存到 {output_file_name}")
