import os
from datetime import datetime, timedelta
from openpyxl import load_workbook

# 假设存在一个全局变量来记录最后创建文件夹的时间和名称
last_folder_creation_time = None
last_folder_name = None

# 获取或创建一个文件夹  变换呢？！！
def get_or_create_folder(base_path):
    global last_folder_creation_time
    global last_folder_name
    now = datetime.now()

    # 如果超过10分钟或者没有创建过文件夹，则创建一个新的文件夹
    if not last_folder_creation_time or (now - last_folder_creation_time) > timedelta(minutes=1):
        # 生成文件夹名称，例如 "240404_1546"
        folder_name = now.strftime('%y%m%d_%H%M')
        folder_path = os.path.join(base_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        last_folder_creation_time = now
        last_folder_name = folder_path
        print(f"创建 {last_folder_name} 文件夹")
    return last_folder_name

# 创建文件，如果有相同文件名称则追加 01
def create_unique_filename(base_path, user_name):
    # 使用下划线替换用户名中的空格
    user_name = user_name.replace(" ", "_")
    filename = f"{user_name}.xlsx"
    index = 1

    while os.path.exists(os.path.join(base_path, filename)):
        filename = f"{user_name}_{str(index).zfill(2)}.xlsx"
        index += 1
    
    return filename

# 创建 xlsx 文件
def create_xlsx_file(row, order_info):
    workbook = load_workbook(filename='sample2.xlsx')  # 确保此处是你的模板文件名
    sheet = workbook.active  # 获取活动工作表
    '''
    print('create_xlsx_file 函数内部')
    print('row 开始')
    print (row)
    print('order_info')
    print (order_info)
    '''

    # 客人姓名
    cell_to_replace_1 = 'B16'  # 确保这是你需要替换内容的正确单元格位置
    user_name = f"{row['First Name']} {row['Last Name']}"

    #总价格
    cell_to_replace_2 = 'E19' 
    user_price = int(float(order_info['totalPrice']))

    #酒店名称
    cell_to_replace_3 = 'B20'
    user_hotel = order_info['hotelName']

    #check In / Out
    cell_to_replace_4 = 'B21'
    cell_to_replace_5 = 'B22'
    user_checkIn = order_info['checkIn']
    user_checkOut = order_info['checkOut']

    #Pax 人数
    cell_to_replace_6 = 'B23'
    #- 成人数量: {order_info['bookingDetails'][0]['customerInfos'][0]['numberOfAdults']}
    #- 儿童数量: {order_info['bookingDetails'][0]['customerInfos'][0]['numberOfChildren']}
    user_pax = f"Adult : {order_info['bookingDetails'][0]['customerInfos'][0]['numberOfAdults']}"

    #订单号
    cell_to_replace_7 = 'B24'
    user_order_no = order_info['orderNo']
    # 替换单元格内容
    sheet[cell_to_replace_1] = user_name
    sheet[cell_to_replace_2] = user_price
    sheet[cell_to_replace_3] = user_hotel
    sheet[cell_to_replace_4] = user_checkIn
    sheet[cell_to_replace_5] = user_checkOut
    sheet[cell_to_replace_6] = user_pax
    sheet[cell_to_replace_7] = user_order_no

    # 假设base_path是你想保存文件的路径
    base_path = "."  # 当前目录
    base_path = get_or_create_folder(base_path)
    # 获取唯一的文件名
    unique_filename = create_unique_filename(base_path, user_name)

    # 保存新的工作簿到动态创建的文件名
    workbook.save(filename=os.path.join(base_path, unique_filename))
    
    send_file = f"{base_path}/{unique_filename}"
    
    # 输出已创建的文件名
    print(f"File created: {unique_filename}")

    #输出要发送的附件路径名称
    return send_file

