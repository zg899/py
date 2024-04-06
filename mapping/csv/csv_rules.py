import pandas as pd
import time
from tqdm import tqdm
from geopy.distance import geodesic
import numpy as np
import chardet
from room_rules import preprocess_name_kr, preprocess_name_jp, compare_smoke_types, check_smoking_rule, check_max_occupancy, compare_areas, compare_bed_codes, compare_bed_numbers


def read_excel(filename, sheet_name=None):
    """读取 Excel 文件"""
    return pd.read_excel(filename, sheet_name=sheet_name)

def read_csv(filename):
    """读取 CSV 文件"""

    return pd.read_csv(filename, sep='\t', on_bad_lines='skip')  # 假设分隔符为制表符

def save_csv(df, filename):
    """将 DataFrame 保存到 CSV 文件，显示进度"""
    start_time = time.time()
    print(f"开始保存到 {filename}")
    df.to_csv(filename, index=False)
    end_time = time.time()
    print(f"完成保存到 {filename}，耗时 {end_time - start_time:.2f} 秒")
   

# 读取csv文件
# mather_code 不为空 且 out_room_type_code包含 Rtx
# 统计数量
# 导出 csv

def filter_and_export_csv(input_csv_path, output_csv_path):
    # 1. 读取 CSV 文件
    df = pd.read_csv(input_csv_path, sep='\t', on_bad_lines='skip')
   
    # 2. 过滤数据
    # 确保 mather_code 不为空且 out_room_type_code 包含 "Rtx"
    filtered_df = df[df['mather_code'].notna() & df['out_room_type_code'].str.contains("Rtx", na=False)]
    
    # 3. 统计数量
    count = len(filtered_df)
    print(f"满足条件的数据总数为: {count}")
    
    # 4. 导出数据到新的 CSV 文件
    filtered_df.to_csv(output_csv_path, index=False)
    print(f"已将过滤后的数据导出到 {output_csv_path}")


    
def merge_dataframes(df1, df2, key=None, left_on=None, right_on=None):
    """合并两个 DataFrame"""
    return pd.merge(df1, df2, how='left', on=key, left_on=left_on, right_on=right_on)

def filter_and_map_data(df, mapping_df, channel, new_columns):
    """筛选并映射数据"""
    filtered_mapping_df = mapping_df[(mapping_df['channel'] == channel)]
    merged_df = pd.merge(df, filtered_mapping_df, how='left', left_on='hotelid', right_on='out_hotel_code')
    return merged_df[new_columns]
    
def count_rows(df):
    """返回数据行数"""
    return len(df)
    
def calculate_statistics(df, column_name):
    """计算指定列的统计数据（平均值、最大值、最小值）"""
    stats = {
        'mean': df[column_name].mean(),
        'max': df[column_name].max(),
        'min': df[column_name].min(),
    }
    return stats

# csv 转换成 excel 
def convert_csv_to_xlsx(input_csv_path, output_xlsx_path, original_sep='\t'):
    # 读取 CSV 文件
    df = pd.read_csv(input_csv_path, sep=original_sep)

    # 导出到 XLSX 文件
    df.to_excel(output_xlsx_path, index=False, engine='openpyxl')


# 比较文本相似度，不考虑大小写，单词顺序
def calculate_similarity(text1, text2):
    text1 = str(text1).lower().split()
    text2 = str(text2).lower().split()
    
    words1 = set(text1)
    words2 = set(text2)
    common_words = words1.intersection(words2)
    total_words = words1.union(words2)
    if len(total_words) == 0:  # 避免除以零
        return 0
    return len(common_words) / len(total_words) * 100

# 以下是经纬度确认逻辑

def is_valid_jp_kr_latitude(lat):
    """
    检查给定的纬度值是否在日本或韩国的有效纬度范围内。
    日本和韩国的纬度范围大致在24°到46°之间。
    """
    return 24 <= lat <= 46

def is_valid_jp_kr_longitude(lon):
    """
    检查给定的经度值是否在日本或韩国的有效经度范围内。
    日本和韩国的经度范围大致在122°到153°之间。
    """
    return 122 <= lon <= 153

def swap_if_reversed_and_validate(lat, lon):
    """
    如果纬度和经度值显然被写反了（例如，纬度值在经度的有效范围内，而经度值在纬度的有效范围内），
    则交换它们。同时检查调整后的值是否在日本或韩国的有效范围内。
    """
    if (122 <= lat <= 153) and (24 <= lon <= 46):
        # 交换纬度和经度
        lat, lon = lon, lat
    # 检查是否在日本或韩国的范围内
    if is_valid_jp_kr_latitude(lat) and is_valid_jp_kr_longitude(lon):
        return lat, lon
    else:
        return None, None

def calculate_distance(latlon1, latlon2, row_index=None):
    """
    计算两个经纬度点之间的距离。首先尝试纠正可能写反的经纬度值，并确保它们在日本或韩国的范围内。
    如果经纬度值无效，返回np.nan。
    """
    try:
        lat1, lon1 = map(float, latlon1)
        lat2, lon2 = map(float, latlon2)
    except ValueError:
        # 如果转换失败，返回np.nan表示这行数据存在问题
        return np.nan

    # 尝试纠正可能写反的经纬度，并验证是否在日本或韩国范围内
    lat1, lon1 = swap_if_reversed_and_validate(lat1, lon1)
    lat2, lon2 = swap_if_reversed_and_validate(lat2, lon2)

    # 如果纠正或验证失败（返回None），则视为无效数据
    if lat1 is None or lat2 is None:
        return np.nan

    # 如果所有检查都通过，则计算并返回两点之间的距离
    return geodesic((lat1, lon1), (lat2, lon2)).meters


# 邮编是否相同
def compare_zipcodes(zip1, zip2):
    """比较两个邮编是否相同。"""
    return zip1 == zip2


# 处理名称相似度，地址相似度，经纬度距离，邮编一致性
def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # 筛选出 hotel_code 不为空的行
    df_not_empty = df[df['hotel_code'].notna()]
    
    # 应用逻辑前确保处理空值，例如使用 fillna
    df_not_empty.fillna('', inplace=True)

    # 计算名称和地址的相似度
    df_not_empty['name_similarity'] = df_not_empty.apply(lambda row: calculate_similarity(row['sup_name'], row['zyx_name']), axis=1)
    df_not_empty['add_similarity'] = df_not_empty.apply(lambda row: calculate_similarity(row['sup_add'], row['zyx_add']), axis=1)
    
    # 计算距离，注意处理可能的异常，例如无效的经纬度值
    df_not_empty['distance_meters'] = df_not_empty.apply(lambda row: calculate_distance((row['sup_lat'], row['sup_long']), (row['zyx_lat'], row['zyx_long'])), axis=1)
    
    # 比较邮编
    df_not_empty['zipcode_match'] = df_not_empty.apply(lambda row: compare_zipcodes(row['sup_post'], row['zyx_post']), axis=1)
    
    # 将修改后的数据（只包含hotel_code不为空的行）保存到新的 CSV 文件
    df_not_empty.to_csv(output_csv, index=False)
    

# 分割文件
# 名称100%相同，距离小于100米，邮编相同的为 OK 
# 否则是 Check 需要人工审核

def filter_and_export_csv(input_csv, ok_csv, check_csv):

    # 使用chardet检测文件编码
    with open(input_csv, 'rb') as file:
        result = chardet.detect(file.read())
        encoding = result['encoding']
    
    # 使用检测到的编码读取CSV文件
    df = pd.read_csv(input_csv, encoding=encoding)
    # 读取CSV文件
    # df = pd.read_csv(input_csv)
    
    # 将 distance_meters 列转换为数值类型，无法转换的设置为 NaN
    df['distance_meters'] = pd.to_numeric(df['distance_meters'], errors='coerce')

    # 筛选满足所有条件的行
    ok_condition = (df['name_similarity'] == 100) & \
                   (df['distance_meters'] < 100) & \
                   (df['zipcode_match'] == True)
    ok_df = df[ok_condition]

    # 筛选不满足至少一个条件的行
    check_df = df[~ok_condition]

    # 导出满足条件的数据到CSV文件
    ok_df.to_csv(ok_csv, sep='\t', index=False, encoding='utf-8')

    # 导出不满足条件的数据到CSV文件
    check_df.to_csv(check_csv, sep='\t', index=False, encoding='utf-8')


# 房型分割函数
# 1，正确聚合房型  2，不正确房型  3，未聚合房型
def zyx_all_room_check_csv(input_csv, ok_csv, check_csv, no_mather_csv):
    start_time = time.time()
    
    ######### 第一步 ： 确认房型文件数据
    # nrows=10000
    # data = pd.read_csv(input_csv, delimiter='\t', encoding='utf-8')
    data = pd.read_csv(input_csv, delimiter='\t', encoding='utf-8', low_memory=False)

    total_count = len(data)
    
    # 显示最前5条数据
    print(data.head())

    # 显示最后5条数据
    print(data.tail())

    # 统计韩国和日本酒店数量
    kr_hotels = data[data['hotel_code'].str.startswith('KR')]
    jp_hotels = data[data['hotel_code'].str.startswith('JP')]

    # 统计有无母房型的数据
    with_mather = data[data['mather_code'].str.startswith('R', na=False)]
    without_mather = data[data['mather_code'].isna() | (data['mather_code'] == '')]

    # 统计各个供应商的数据
    jtb_count = data['out_room_type_code'].str.contains('JTB').sum()
    rtx_count = data['out_room_type_code'].str.contains('Rtx').sum()
    jalan_count = data['out_room_type_code'].str.contains('Jalan').sum()
    ynj_count = data['out_room_type_code'].str.contains('Yanolja').sum()

    # 打印统计结果
    print(f"一共导入{total_count}条数据。")
    print(f"其中韩国酒店 {len(kr_hotels)}条，占比{(len(kr_hotels)/total_count*100):.2f}%")
    print(f"日本酒店 {len(jp_hotels)}条，占比{(len(jp_hotels)/total_count*100):.2f}%")
    print(f"有母房型数据 {len(with_mather)}，占比{(len(with_mather)/total_count*100):.2f}%")
    print(f"无母房型数据{len(without_mather)}，占比{(len(without_mather)/total_count*100):.2f}%")
    print(f"JTB {jtb_count}，占比{(jtb_count/total_count*100):.2f}%")
    print(f"RTX {rtx_count}，占比{(rtx_count/total_count*100):.2f}%")
    print(f"JALAN {jalan_count}，占比{(jalan_count/total_count*100):.2f}%")
    print(f"YNJ {ynj_count}，占比{(ynj_count/total_count*100):.2f}%。")
    
    input("7-1 处理完毕，回车继续 7-2 ：名称处理")
    
    ########## 第二步 ： 确认名称是否相同
    
    # 处理房型名称
    def compare_processed_names(son, mather):
    # 将字符串转换为小写并分割为单词列表
        son_words = sorted(str(son).lower().split())
        mather_words = sorted(str(mather).lower().split())
        return son_words == mather_words
    def find_mismatched_words(son, mather):
        son_words_set = set(str(son).lower().split())
        mather_words_set = set(str(mather).lower().split())
    
        # 找到不匹配的单词
        son_other_words = son_words_set - mather_words_set
        mather_other_words = mather_words_set - son_words_set
    
        # 将结果转换为逗号分隔的字符串
        son_other_words_str = ", ".join(son_other_words)
        mather_other_words_str = ", ".join(mather_other_words)
    
        return son_other_words_str, mather_other_words_str

    tqdm.pandas(desc="处理进度")
    data['son_processed'] = data.progress_apply(lambda x: preprocess_name_kr(x['son_name']) if x['hotel_code'].startswith('KR') else preprocess_name_jp(x['son_name']), axis=1)
    data['mather_processed'] = data.progress_apply(lambda x: preprocess_name_kr(x['mather_name']) if x['hotel_code'].startswith('KR') else preprocess_name_jp(x['mather_name']), axis=1)  
    # 直接使用比较结果更新DataFrame
    data['names_match'] = data.apply(lambda x: compare_processed_names(x['son_processed'], x['mather_processed']), axis=1)
    # 子母房型是否匹配状态变量
    names_match_results = data['names_match']
    # 应用函数并创建新列
    data[['son_other_words', 'mather_other_words']] = data.apply(lambda x: find_mismatched_words(x['son_processed'], x['mather_processed']), axis=1, result_type='expand')

    
    # 导出到temp.csv 
    # data.to_csv('temp.csv', columns=['son_processed', 'mather_processed'], sep='\t', index=False, encoding='utf-8') # 只导出   columns=['son_processed', 'mather_processed']
    # 导出到temp.csv，包括所有原始数据列和处理后的两列
    input("7-2 处理完毕，回车继续 7-3 : 吸烟属性处理")
    
    ######### 第三步 ： 确认吸烟属性
    
    # 调用吸烟信息对比函数
    tqdm.pandas(desc="处理进度")
    data['smoke_type_match'] = data.progress_apply(lambda x: compare_smoke_types(x['mather_smoke'], x['son_smoke']), axis=1)
    
    # 吸烟属性状态变量
    smoke_type_match = data['smoke_type_match']
    # 调用吸烟名称规则检查函数
    tqdm.pandas(desc="处理进度")
    data['smoke_name_match'] = data.progress_apply(lambda x: check_smoking_rule(x['mather_name'], x['son_name']), axis=1)
    # 吸烟名称状态变量
    smoke_name_match = data['smoke_name_match']
    
    input("7-3 处理完毕，回车继续 7-4 : 最大入住人数处理")
    
    ########### 第四步 ： 确认房型最大入住人数
    tqdm.pandas(desc="处理进度")
    data['max_check'] = data.progress_apply(lambda x: check_max_occupancy(x['mather_max'], x['son_max']), axis=1)
    #最大入住人数判断变量
    max_check = data['max_check']
    input("7-4 处理完毕，回车继续 7-5 : 房间面积处理")
    
    ########### 第五步 ： 确认房型面积
    tqdm.pandas(desc="处理面积")
    data['area_check'] = data.progress_apply(lambda x: compare_areas(x['mather_area'], x['son_area']), axis=1)
    
    #面积确认变量
    area_check = data['area_check']
    input("7-5 处理完毕，回车继续 7-6 : 床型代码处理")
    
    ########### 第六步 ： 确认房型床代码  
    tqdm.pandas(desc="正在处理床代码")
    data['check_bed_code'] = data.progress_apply(lambda x: compare_bed_codes(x['mather_bed_code'], x['son_bed_code']), axis=1)
    checn_bed_code = data['check_bed_code']
    input("7-6 处理完毕，回车继续 7-7 : 床型数量处理")
    
    # 第七步 ： 确认房型床数量
    tqdm.pandas(desc="正在处理床数量")
    data['check_bed_number'] = data.progress_apply(lambda x: compare_bed_numbers(x['mather_bed_number'], x['son_bed_number']), axis=1)
    check_bed_number = data['check_bed_number']
    input("7-7 处理完毕，回车继续 7-8 : 整合上述条件并分类文件")
    # 第八步 ： 整合判断上述条件
    
    # 分组保存的函数
    def save_filtered_data(data, condition, prefix, true_filename, false_filename):
        """
        根据条件和前缀筛选数据并保存到指定的文件。
        """
        filtered_data = data[data['hotel_code'].str.startswith(prefix)]
        filtered_data[condition].to_csv(true_filename, sep='\t', index=False, encoding='utf-8')
        filtered_data[~condition].to_csv(false_filename, sep='\t', index=False, encoding='utf-8')

    # 定义一个条件，所有状态变量都为True
    all_true_condition = (data['names_match'] == True) & \
                         (data['smoke_type_match'] == True) & \
                         (data['max_check'] == True) & \
                         (data['area_check'] == True) & \
                         (data['check_bed_code'] == True) & \
                         (data['check_bed_number'] == True)

    # 根据hotel_code前缀和条件分别保存数据
    
    save_filtered_data(data, all_true_condition, 'KR', 'KR_rooms_true.csv', 'KR_rooms_false.csv')  
    save_filtered_data(data, all_true_condition, 'JP', 'JP_rooms_true.csv', 'JP_roomss_false.csv')
    
    input("7-8 处理完毕，回车继续 7-9 : 创建无母房型的子房型")
    # 第九步 ： 筛选出无母房型的数据

    without_mather = data[data['mather_code'].isna() | (data['mather_code'] == '')]
    # 导出无母房型的数据到CSV文件
    without_mather.to_csv('without_mather_rooms.csv', sep='\t', index=False, encoding='utf-8')
    
    print("创建完毕！任务结束！")   
    # 计算执行时间
    end_time = time.time()
    print(f"执行时间：{end_time - start_time}秒。") 