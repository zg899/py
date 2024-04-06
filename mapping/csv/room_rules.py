# 文件名: room_rules.py
# room mapping 相关函数库

import pandas as pd
import re
from collections import Counter
from tqdm import tqdm
from datetime import datetime
import csv
from tqdm.auto import tqdm
import json
import time

# 定义需要去除的房型名称字符作为全局变量 
# 日本酒店
with open('un_jp0310.json', 'r') as file:
    remove_room_keywords_jp = json.load(file)
    #print(remove_room_keywords)

# 定义需要去除的房型名称字符作为全局变量 
# 韩国酒店
with open('un_kr0309.json', 'r') as file:
    remove_room_keywords_kr = json.load(file)

# 定义吸烟和非吸烟的关键词作为全局变量
smoking_keywords = [
    'smoking', 'smoking room', 'smoke', 'smokoing', 'smoki', 'smokinng',
    '(smokin', 'smokling'
]
nonsmoking_keywords = [
    'no smoking', 'No smoking', 'non smoking', 'no-smoking', 'non-smoking', 'nonsmoking',
    'non smoke', 'no smoki', 'nonsmoke', 'non-smokng', 'no smokin', 'non-smoki',
    'no smok', 'non smokin', 'non-smok', 'non smokimg', 'non smoki', 'smokiing', 'Non Smoking Room',
    'nosmokin'
]
# 如果房型只有这些单词就保留
single_keywords = ['room','standard'] # 如果房型只有这些单词就保留

# 此单词必须单独出现 才能移除
except_adjacent_keywords = ['room'] 


# 清理文字 
# → , + , -,: 
def preprocess_text3(text):
    # 确保输入是字符串类型
    if pd.isna(text):
        text = ""  # 如果是NaN，替换为空字符串
    else:
        text = str(text)  # 确保其他非字符串类型的值被转换为字符串
    
    # 如果 - 符号在文本开头，删除它
    text = re.sub(r'^-', '', text)
    
    # 去除所有符号，保留字母、数字、空格和中间的 - 符号
    # 使用空格替代被去除的所有符号
    text = re.sub(r'[^\w\s-]|_', ' ', text)
    
    # 所有内容变成小写
    text = text.lower()
    
    # 所有文本中的多个空格(包括由于去除符号产生的)变成单空格
    text = re.sub(r'\s+', ' ', text)
    
    # 文本前后去掉空格
    text = text.strip()

    return text


# 清理文字 KR版,貌似JP用也没问题，3.11周一再确认 
# →, +, :,-,.,',%,㎡,/,& 
def preprocess_text_kr(text):
    # 确保输入是字符串类型
    if pd.isna(text):
        text = ""  # 如果是NaN，替换为空字符串
    else:
        text = str(text)  # 确保其他非字符串类型的值被转换为字符串
    
    # 除了 →, +, :,-,.,',%,㎡,/,& 这十个符号之外的其他所有符号清除
    # 注意：在正则表达式中使用\来转义特殊字符，如+和-
    text = re.sub(r'[^\w\s\→\+\-\:\.\'\%\㎡\/\&]', ' ', text)
    
    # 所有内容变成小写
    # text = text.lower()
    
    # 所有文本中的多个空格(包括由于去除符号产生的)变成单空格
    text = re.sub(r'\s+', ' ', text)
    
    # 文本前后去掉空格
    text = text.strip()

    return text
    
# 检查是否包含关键词函数
def contains_keywords(text, keywords):
    """检查文本是否包含任何关键词。"""
    return any(keyword in text.lower() for keyword in keywords)

# 吸烟信息是否一致函数 ，确认吸烟状态
# 空，0，无吸烟信息
# 1 禁烟房 NO Smoking
# 2 吸烟房 Smoking  
def compare_smoke_types(mather_smoke, son_smoke):
    # Function to process each smoke value
    def process_value(value):
        # Check for empty or NaN values and treat them as '0'
        if pd.isna(value) or value == '':
            return 0
        try:
            # First, convert to float to handle values like '1.0', then convert to int
            value_int = int(float(value))
            if value_int in {0, 1, 2}:
                return value_int
            else:
                # If value is outside of the expected range, return 'error'
                return "error"
        except ValueError:
            # If conversion fails, return 'error'
            return "error"

    mather_smoke_processed = process_value(mather_smoke)
    son_smoke_processed = process_value(son_smoke)

    # Check for 'error' in processed values
    if "error" in [mather_smoke_processed, son_smoke_processed]:
        return "error"
    # Compare the processed values for equality
    return mather_smoke_processed == son_smoke_processed


# 确认吸烟信息是否一致函数，两个都没有吸烟信息就输出空
# 用名称比较
def check_smoking_rule(mather_name, son_name):
    # 确保输入是字符串类型
    mather_name = str(mather_name) if not pd.isna(mather_name) else ''
    son_name = str(son_name) if not pd.isna(son_name) else ''
    
    #清理多余字符
    mather_name = preprocess_text3(mather_name)
    son_name = preprocess_text3(son_name)

    # 检查母房型和子房型是否都包含吸烟或非吸烟关键词
    mather_smoking = contains_keywords(mather_name, smoking_keywords)
    son_smoking = contains_keywords(son_name, smoking_keywords)
    mather_nonsmoking = contains_keywords(mather_name, nonsmoking_keywords)
    son_nonsmoking = contains_keywords(son_name, nonsmoking_keywords)
    
     # 检查是否母房型和子房型都没有吸烟信息
    if not (mather_smoking or son_smoking or mather_nonsmoking or son_nonsmoking):
        return ("None")  # 如果都没有吸烟信息，则输出 None
    
    # 如果母房型和子房型的吸烟状态一致，则返回True
    return mather_smoking == son_smoking and mather_nonsmoking == son_nonsmoking

# 加载单词库函数 。必要单词库。
def load_necessity_words(file_path):
    df_necessity = pd.read_excel(file_path, sheet_name='Necessity')
    necessity_words = set()
    for column in df_necessity:
        necessity_words.update(df_necessity[column].dropna().str.lower().tolist())
    return necessity_words

# 确认子母房型是否匹配函数，基于单词库，不分大小写
def check_match(mather_name, son_name, necessity_words):
    mather_name = str(mather_name)
    son_name = str(son_name)
    mather_words = set(mather_name.lower().split())
    son_words = set(son_name.lower().split())
    return mather_words == son_words and mather_words.issubset(necessity_words)


# 去除 room,Room 吸烟属性单词后 变成全部小写，不分顺序的比较是否一致。
# preprocess_text(text): 重复了，修改成 preprocess_room
# 原来函数名称 
def preprocess_room(text):
    """预处理文本，移除'room'单词和吸烟相关单词，不区分大小写，返回单词计数"""
    # 定义要移除的单词列表，这里只示例了几个可能的吸烟属性单词
    remove_words = ['room', 'Room', smoking_keywords, nonsmoking_keywords]
    words = [word for word in text.lower().split() if word not in remove_words]
    return Counter(words)


# 移除单词v2
def preprocess_name2(name, remove_room_keywords, smoking_keywords, nonsmoking_keywords):

    # 如果输入不是字符串（例如NaN，被识别为float），则转换为字符串
    # name = "" if pd.isna(name) else str(name)
    
    # 清洗房型数据
    name = preprocess_text3(name); # 日本酒店房型用这个函数去除符号
    # name = preprocess_text_kr(name); # 韩国酒店房型用这个函数去除符号
    # 合并所有需要移除的关键词列表
    
    remove_words = remove_room_keywords + smoking_keywords + nonsmoking_keywords
    # 转换为小写并移除不需要的单词，不考虑排序
    words = name.split()
    processed_words = set([word.lower() for word in words if word.lower() not in [x.lower() for x in remove_words]])
    return processed_words


# 移除单词 韩国酒店 
# 原来函数，目前不用，参考用
def preprocess_name_kr2(name, remove_room_keywords, smoking_keywords, nonsmoking_keywords):

    # 如果输入不是字符串（例如NaN，被识别为float），则转换为字符串
    # name = "" if pd.isna(name) else str(name)
    
    # 清洗房型数据
    # name = preprocess_text3(name); # 日本酒店房型用这个函数去除符号
    name = preprocess_text_kr(name); # 韩国酒店房型用这个函数去除符号
    # 合并所有需要移除的关键词列表
    
    remove_words = remove_room_keywords_kr + smoking_keywords + nonsmoking_keywords
    # 转换为小写并移除不需要的单词，不考虑排序
    words = name.split()
    processed_words = set([word.lower() for word in words if word.lower() not in [x.lower() for x in remove_words]])
    return processed_words

# 移除单词 韩国酒店 
# 保持原来单词顺序，恢复大小写

def preprocess_name_kr(name):
    # 如果输入不是字符串（例如NaN，被识别为float），则转换为字符串
    name = "" if pd.isna(name) else str(name)
    
    # 预处理文本以去除符号，此步骤保留原始大小写
    name_processed = preprocess_text_kr(name)
    
    # 合并所有需要移除的关键词列表
    remove_phrases = remove_room_keywords_kr + smoking_keywords + nonsmoking_keywords
    
    # 转换为小写进行比较，同时保留原始文本用于最终输出
    name_lower = name_processed.lower()
    
    # 移除非必要的短语或单词，不考虑大小写
    for phrase in remove_phrases:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        name_lower = pattern.sub('', name_lower)
    
    # 根据处理后的小写文本重新构建原始大小写文本
    words_processed = name_processed.split()
    words_lower = name_lower.split()
    final_words = []
    
    for word in words_processed:
        if word.lower() in words_lower:
            final_words.append(word)
            words_lower.remove(word.lower())
            
    # 将处理后保留的单词列表转换回字符串形式，保留原始大小写和单词顺序
    final_text = ' '.join(final_words)

    # 删除最前面或最后面的 →, +, -, : 符号
    final_text = re.sub(r'^[\→\+\-\:]+|[\→\+\-\:]+$', '', final_text)
    return final_text


# 移除单词 日本酒店 
# 保持原来单词顺序，恢复大小写

def preprocess_name_jp(name):
    # 确保输入是字符串类型
    name = "" if pd.isna(name) else str(name)

    # 预处理文本以去除符号，此步骤保留原始大小写
    name_processed = preprocess_text_kr(name)
    
    # 合并所有需要移除的关键词列表
    remove_phrases = remove_room_keywords_jp + smoking_keywords + nonsmoking_keywords
    
    # 按短语长度从长到短排序
    remove_phrases_sorted = sorted(remove_phrases, key=len, reverse=True)
    
    # 转换为小写进行比较，同时保留原始文本用于最终输出
    name_lower = name_processed.lower()
    original_name_lower = name_lower  # 保存原始处理后的小写文本以备后用
    
    # 移除非必要的短语或单词，不考虑大小写
    for phrase in remove_phrases_sorted:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        name_lower = pattern.sub('', name_lower)
    
    # 如果删除完毕后结果为空，则保留原来去除符号后的房型名称
    if not name_lower.strip():
        name_lower = original_name_lower
    
    # 根据处理后的小写文本重新构建原始大小写文本
    words_processed = name_processed.split()
    words_lower = name_lower.split()
    final_words = []

    for word in words_processed:
        if word.lower() in words_lower:
            final_words.append(word)
            words_lower.remove(word.lower())

    # 将处理后保留的单词列表转换回字符串形式，保留原始大小写和单词顺序
    final_text = ' '.join(final_words)

    # 删除最前面或最后面的 →, +, -, : 符号
    final_text = re.sub(r'^[\→\+\-\:]+|[\→\+\-\:]+$', '', final_text)
    
    return final_text

# 0304 17:34
# 是否判断吸烟属性控制器
# require_smoking_consistency=False 不看吸烟属性
# require_smoking_consistency=True 同时确认吸烟属性
 
def find_matching_mather_codes(df, check_smoking_rule, smoking_keywords, nonsmoking_keywords, require_smoking_consistency=True):
    result = []  # 用于存储找到的符合条件的索引和mather_code
    print("开始遍历DataFrame的每一行...")
    
    # 使用tqdm包装df.iterrows()来添加进度条
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="处理进度"):
        # 根据require_smoking_consistency参数决定是否只处理吸烟规则不一致的行
        if not require_smoking_consistency or (require_smoking_consistency and row['smoking_rule_consistent'] == False):
            # 找到同一酒店代码的所有行
            group = df[df['hotel_code'] == row['hotel_code']]
            # 排除当前母房型的其他行
            others = group[group['mather_code'] != row['mather_code']]
            # 打印当前处理的行信息
            print(f"正在处理 {row['hotel_code']} 的行，索引为 {index}...")
            # 遍历可能的母房型
            for _, other_row in others.iterrows():
                # 如果不需要检查吸烟属性一致性或检查后吸烟属性一致
                if not require_smoking_consistency or (require_smoking_consistency and check_smoking_rule(row['son_name_processed'], other_row['mather_name_processed'])):
                    # 移除指定的单词后进一步比较名称属性
                    son_processed = preprocess_name2(row['son_name_processed'], remove_room_keywords, smoking_keywords, nonsmoking_keywords)
                    mather_processed = preprocess_name2(other_row['mather_name_processed'], remove_room_keywords, smoking_keywords, nonsmoking_keywords)
                    
                    # 如果名称属性一致
                    if son_processed == mather_processed:
                        print(f"找到匹配的母房型：{other_row['mather_code']} 对应的索引为 {index}")
                        result.append((index, other_row['mather_code']))
                        break
    
    # 打印匹配结果的总数
    print(f"总共找到 {len(result)} 个匹配的母房型。")
    
    # 更新DataFrame
    if 'matching_mather_code' not in df.columns:
        df['matching_mather_code'] = pd.NA
    for index, mather_code in result:
        df.at[index, 'matching_mather_code'] = mather_code
    
    return df

# 0306 20:04
# 另一个寻找母房型函数
# 是否确认房型名称里面的 吸烟相关单词判断函数
# require_smoking_consistency=False 不看名称吸烟属性
# require_smoking_consistency=True 同时确认名称吸烟属性
# 待完善 0306 20:20
# 完成：未聚合的子房型，寻找母房型功能 
# 0310 12:32 修改版，先找母房型，再找是否匹配吸烟属性
def find_matching_mather_codes2(df, preprocess_name_type='kr'):
    if preprocess_name_type == 'jp':
        preprocess_name_Ctype = preprocess_name_jp
    elif preprocess_name_type == 'kr':
        preprocess_name_Ctype = preprocess_name_kr
    else:
        raise ValueError("Invalid preprocess name type. Use 'jp' or 'kr'.")

    start_time = time.time()  # 记录开始时间
    # df = df.head(1000)  # 限制数据集为前10000条数据进行测试
    df = df.copy()  # 假设 df 是通过筛选或切片另一个 DataFrame 得到的
    unique_hotel_codes = df['hotel_code'].nunique()
    print(f"一共找到了 {unique_hotel_codes} 个酒店code。")
    
    mather_code_empty_count = df[pd.isna(df['mather_code']) | (df['mather_code'] == '')].shape[0]
    print(f"一共找到了 {mather_code_empty_count} 个母房型code为空的子房型。")
    
    new_mather_codes = pd.Series(index=df.index, dtype='object')
    new_mather_names = pd.Series(index=df.index, dtype='object')
    new_mather_smoke = pd.Series(index=df.index, dtype='object')

    grouped = df.groupby('hotel_code')
    
    for hotel_code, group in tqdm(grouped, total=grouped.ngroups, desc="正在处理酒店"):  # 为酒店分组迭代添加进度条
        for index, row in group.iterrows():  # 遍历每个酒店的所有行
            if pd.isna(row['mather_code']) or row['mather_code'] == '':
                # 对每一个子房型名称进行预处理
                son_name_processed = preprocess_name_Ctype(row['son_name'])
                found_match = False
                
                for _, potential_mather_row in group.iterrows():
                    # 对每一个可能的母房型名称进行预处理
                    mather_name_processed = preprocess_name_Ctype(potential_mather_row['mather_name'])
                    # 首先判断处理后的名称是否一致
                    if son_name_processed == mather_name_processed:
                        # 如果名称一致，再检查吸烟属性是否匹配
                        smoke_param_match = compare_smoke_types(row['son_smoke'], potential_mather_row['mather_smoke'])
                        if smoke_param_match:
                            new_mather_codes.at[index] = potential_mather_row['mather_code']
                            new_mather_names.at[index] = potential_mather_row['mather_name']
                            new_mather_smoke.at[index] = potential_mather_row['mather_smoke']
                            found_match = True
                            break  # 找到匹配项，跳出内层循环
                 
    df.loc[new_mather_codes.index, 'New_mather_code'] = new_mather_codes
    df.loc[new_mather_names.index, 'New_mather_name'] = new_mather_names
    df.loc[new_mather_smoke.index, 'New_mather_smoke'] = new_mather_smoke
    non_empty_new_mather_count = new_mather_codes.notna().sum()
    print(f"一共找到了 {non_empty_new_mather_count} 个匹配的母房型。")
    end_time = time.time()
    print(f"完成所有处理，总耗时: {end_time - start_time:.2f}秒")
    
    return df


    
# 定义处理和比较名称的函数（加入了 preprocess_text 的调用）
def normalize_and_compare_names(son_name, mother_name):
    # 使用 room_rules.py 中定义的 preprocess_text 函数预处理名称
    def normalize_name(name):
        # 预处理文本，去除多余字符
        cleaned_name = preprocess_text3(name)
        # 去除非必要单词
        for word in remove_room_keywords:  # 使用从 room_rules 导入的全局变量
            cleaned_name = cleaned_name.replace(word, '')
           # print(cleaned_name)
        # 分割为单词列表并去重排序，确保比较时不考虑顺序
        word_list = sorted(set(cleaned_name.split()))
        return ' '.join(word_list)
    
    # 规范化名称
    normalized_son_name = normalize_name(son_name)
    normalized_mother_name = normalize_name(mother_name)
    
    #print(normalized_son_name)
    #print(normalized_mother_name)
   
    # 比较并返回结果
    if normalized_son_name == normalized_mother_name:
        return True, ""
    else:
        # 计算不匹配的部分
        diff = set(normalized_son_name.split()) ^ set(normalized_mother_name.split())
        return False, diff




# 加载JSON 样板 - 目前不用 
'''
with open('unNesskr0308j.json', 'r') as file:
    keywords = json.load(file)
'''
# 定义预处理函数
def preprocess_text_remove_smoking_keywords(text, keywords):
    if pd.isna(text):
        return ""
    text = text.lower()
    
    # 将三个关键词列表合并为一个
    keywords_to_remove = keywords['remove_room_keywords'] + keywords['smoking_keywords'] + keywords['nonsmoking_keywords']
    
    for keyword in keywords_to_remove:
        text = re.sub(r'\b{}\b'.format(re.escape(keyword)), ' ', text)
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
    

    
# 移除单词，成功版！ 0306 v2
def preprocess_text_remove_smoking_and_room(text):
    #print(f"原始文本: {text}")
    # 确保输入是字符串类型
    text = str(text) if not pd.isna(text) else ''
    text = text.lower()
    text = preprocess_text3(text)
    
    # 首先处理特殊的除外关键词（如连字符紧密相连的单词不移除）room 
    for pattern in except_adjacent_keywords:
        text = re.sub(r'(?<!\w)' + re.escape(pattern) + r'(?!\w)', ' ', text, flags=re.IGNORECASE)

    # 处理一般的移除关键词
    all_combined_keywords = remove_room_keywords_kr + smoking_keywords + nonsmoking_keywords
    # 对关键词进行排序，这里考虑关键词的长度，确保长关键词优先被替换
    all_combined_keywords.sort(key=len, reverse=True)
    
    for pattern in all_combined_keywords:
        if pattern not in except_adjacent_keywords:  # 避免重复处理
            text = re.sub(r'\b' + re.escape(pattern) + r'\b', ' ', text, flags=re.IGNORECASE)

    # 针对含有连字符的复合关键词进行特殊处理
    combined_keywords = smoking_keywords + nonsmoking_keywords
    combined_keywords.sort(key=len, reverse=True)
    for keyword in combined_keywords:
        # 替换关键词为空格
        keyword_pattern = r'\b{}\b'.format(re.escape(keyword))
        text = re.sub(keyword_pattern, ' ', text, flags=re.IGNORECASE)
        
        # 特殊处理连字符情况
        if '-' in keyword:
            keyword_pattern = r'\b{}\b'.format(re.escape(keyword).replace('-', r'\-'))
            text = re.sub(keyword_pattern, ' ', text, flags=re.IGNORECASE)

    # 移除额外的空格
    text = re.sub(r'\s+', ' ', text).strip()
    # print(f"去除非必要单词后: {text}")

    return text

# 0307 12:28
#已聚合子母房型确认是否聚合正确
# 1，吸烟名称比较
# 2，房型名称比较
# 3，吸烟属性比较
# 4，最大入住人数确认
# 5，面积对比
# 6，床型和 床数量对比

def validate_mather_son_aggregation(df):
    start_time = time.time()  # 记录函数开始执行的时间

    # 筛选出 mather_code 非空的行，并创建副本以避免 SettingWithCopyWarning
    df_with_mather = df[df['mather_code'].notna() & df['mather_code'].str.startswith('R')] .copy()
    print(f"筛选 mather_code非空的行 {len(df_with_mather)} 条数据。")
    # 初始化新列
    df_with_mather['mapping_state'] = False
    df_with_mather['mather_other_words'] = None
    df_with_mather['son_other_words'] = None
    df_with_mather['smoke_param_check'] = None
    df_with_mather['smoke_name_check'] = None

    # 使用 tqdm 添加进度条
    for index, row in tqdm(df_with_mather.iterrows(), total=df_with_mather.shape[0], desc="验证子母房型聚合"):
        loop_start_time = time.time()  # 记录每次循环开始的时间

        # 执行已有的逻辑
        
        # 吸烟名称判断
        smoke_name_match = check_smoking_rule(row['mather_name'], row['son_name'])
        
        # 吸烟参数判断
        smoke_param_match = compare_smoke_types(row['mather_smoke'], row['son_smoke'])
        
        # 母房型名称符号处理，删除不必要单词
        mather_name_processed = preprocess_text_remove_smoking_and_room(row['mather_name'])
        
        # 子房型名称符号处理，删除不必要单词
        son_name_processed = preprocess_text_remove_smoking_and_room(row['son_name'])
        
        
        mather_words = set(mather_name_processed.lower().split())
        son_words = set(son_name_processed.lower().split())
        
        #处理后的子母名称相同，同时 吸烟参数相同
        # if mather_words == son_words and smoke_param_match: 同时确认 吸烟参数
        if mather_words == son_words:
            df_with_mather.at[index, 'mapping_state'] = True
        else:
            df_with_mather.at[index, 'mapping_state'] = False
            df_with_mather.at[index, 'mather_other_words'] = ", ".join(mather_words - son_words)
            df_with_mather.at[index, 'son_other_words'] = ", ".join(son_words - mather_words)
        
        df_with_mather['smoke_param_check'] = smoke_param_match
        df_with_mather['smoke_name_check'] = smoke_name_match
    
    end_time = time.time()  # 记录函数结束执行的时间
    print(f"完成所有处理，总耗时: {end_time - start_time:.2f}秒")

    return df_with_mather
    
# 最大入住人数，床型，床数量比较
# 0310
def compare_room_features(son_max, mather_max, son_bed_code, mather_bed_code, son_bed_number, mather_bed_number):


    # 1. 最大入住人数比较
    try:
        max_occupancy_comparison = int(son_max) >= int(mather_max)
    except ValueError:
        max_occupancy_comparison = False  # 如果转换失败，则比较结果为False

    # 2. 床型代码比较
    
     # 处理mather_bed_code之前检查它是否为字符串
    if isinstance(mather_bed_code, str):
        mather_bed_code_list = [code.lower() for code in mather_bed_code.split(',')]
    else:
        mather_bed_code_list = []

    # 处理son_bed_code之前检查它是否为字符串
    if isinstance(son_bed_code, str):
        son_bed_code_list = [code.lower() for code in son_bed_code.split(',')]
    else:
        son_bed_code_list = []

    # son_bed_code_list = [code.lower() for code in son_bed_code.split(',')]
    # mather_bed_code_list = [code.lower() for code in mather_bed_code.split(',')]
    # 检查子房型床型是否包含母房型的所有床型（不考虑顺序）
    bed_code_comparison = all(item in son_bed_code_list for item in mather_bed_code_list)

    # 3. 床型数量比较
    try:
        bed_number_comparison = int(son_bed_number) == int(mather_bed_number)
    except ValueError:
        bed_number_comparison = False  # 如果转换失败，则比较结果为False

    return max_occupancy_comparison, bed_code_comparison, bed_number_comparison
    
# 调用函数
# results = compare_room_features(son_max, mather_max, son_bed_code, mather_bed_code, son_bed_number, mather_bed_number)
# print(f"最大入住人数比较: {results[0]}, 床型代码比较: {results[1]}, 床型数量比较: {results[2]}")

# 对比子母房型最大入住人数逻辑
def check_max_occupancy(mather_max, son_max):
    try:
        # 先转换为字符串，然后去除两端空白，最后判断是否为空字符串
        son_max = str(son_max).strip()
        mather_max = str(mather_max).strip()
        # 如果任一值为空字符串，直接返回None
        if not son_max or not mather_max:
            return None
        # 尝试转换为浮点数
        son_max = float(son_max)
        mather_max = float(mather_max)
    except ValueError:  # 如果转换失败，说明不是可转换为数值的字符串
        return None

    # 执行比较逻辑
    if son_max is None or mather_max is None:  # 再次确认是否有空值
        return None
    return mather_max <= son_max

# 对比两个房型的面积
def compare_areas(mather_area, son_area):
    try:
        # 尝试将输入转换为浮点数，以便处理小数点面积
        mather_area = float(mather_area) if mather_area else None
        son_area = float(son_area) if son_area else None
    except ValueError:
        # 如果转换失败，说明至少一个不是有效的数字
        return None

    # 检查是否有一个值为空，这意味着没有可比性
    if mather_area is None or son_area is None:
        return None
    
    # 比较两个面积是否相等
    return mather_area == son_area


# 对比房型CODE 部分

word_equivalence = {
    "other": "others",
    "semi": "semi double"
}

def normalize_word(word):
    word = word.lower()
    return word_equivalence.get(word, word)

def compare_bed_codes(mather_bed_code, son_bed_code):
    # 确保输入值是字符串类型
    mather_bed_code = str(mather_bed_code) if mather_bed_code else ""
    son_bed_code = str(son_bed_code) if son_bed_code else ""

    # 分割、规范化单词并转换成集合
    mather_set = {normalize_word(word) for word in mather_bed_code.lower().split(",")}
    son_set = {normalize_word(word) for word in son_bed_code.lower().split(",")}
    
    # 比较两个集合是否相等
    return mather_set == son_set

# 对比床数量 

def compare_bed_numbers(mather_bed_number, son_bed_number):
    try:
        # 尝试将输入转换为整数
        mather_bed_number = int(mather_bed_number) if mather_bed_number else None
        son_bed_number = int(son_bed_number) if son_bed_number else None
    except ValueError:
        # 如果转换失败，说明至少一个不是有效的数字
        return None

    # 检查是否有一个值为空，这意味着没有可比性
    if mather_bed_number is None or son_bed_number is None:
        return None
    
    # 比较两个数字是否相等
    return mather_bed_number == son_bed_number

