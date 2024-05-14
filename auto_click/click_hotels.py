# click_hotels.py
logPath = r'/logs'  # Linux用

def hotel_url():
    txt_file_name = "url_0514_1.txt"  # 注意路径拼接时需要添加斜杠
    url_1 = "https://www.agoda.com/dormy-inn-maebashi-hot-spring/hotel/maebashi-jp.html?"  # URL地址
    start_date = "2024-11-02"  # 开始日期
    num_days = 1  # 连续确认天数
    los_num = 1  # 连住天数
    adults_num = 1  # 成人数量
    
    hotel_urls = [txt_file_name, url_1, start_date, num_days, los_num, adults_num]

    return hotel_urls
