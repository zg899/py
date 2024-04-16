import requests
import json
from datetime import datetime

# Agent Name
def get_agent_name(agent_code):
    # 定义一个字典来存储agent_code到agent_name的映射
    agent_mapping = {
        "M223011284": "Yanolja-Buy",
        "M219121176": "Agoda",
        "M219081094": "Ctrip_japan(1119)",
        "M219060970": "Fliggy-Japan",
        "M219121196": "Meituan-krw",
        "M223111292": "Fliggy-Hangzhou",
        "M217110390": "Meituan",
        "M218070568": "Qunar",
        "M219050898": "Ctrip_korea(1031)",
        "M218050500": "Ctrip3(665)",
        "M224041306": "Tongcheng"
    }

    # 使用get方法从字典中获取agent_name，如果找不到则返回None
    return agent_mapping.get(agent_code, None)

# 订单状态函数
def get_order_status_description(order_status_code):
    # 定义一个字典，将订单状态代码映射到易读的状态描述
    status_descriptions = {
        "10": " :tada: Confirmed :tada: ",  # 确认
        "30": " :scissors: Canceled :scissors:",  # 已取消
        "70": " :bomb: Cancel Failed!!! :bomb: "  # 取消失败
    }
    return status_descriptions.get(order_status_code, "Unknown Status")
# 日期差函数
def calculate_days_between_dates(check_in, check_out):
    # 将日期字符串转换为datetime对象
    date_format = "%Y-%m-%d"
    check_in_date = datetime.strptime(check_in, date_format)
    check_out_date = datetime.strptime(check_out, date_format)
    
    # 计算两个日期之间的差值，并获取天数
    delta = check_out_date - check_in_date
    return delta.days

# 日本用
def format_order_s(order_info):
    print(f"order_JP 函数 原本订单信息: {order_info}")
    days_difference = calculate_days_between_dates(order_info['checkIn'], order_info['checkOut'])

    order_state = get_order_status_description(order_info['orderStatus'])

    # 准备房型和酒店信息
    room_and_hotel_info_lines = []

    # 检查bookingDetails是否存在且是列表类型
    numberofroom = 0
    if order_info['bookingDetails'] and isinstance(order_info['bookingDetails'], list):
        numberofroom = order_info['bookingDetails'][0].get('numberOfRooms', 0)

    # 遍历orderProductDetails列表
    for product in order_info.get('orderProductDetails', []):
        room = product.get('room', {})
        room_name = room.get('name', 'Unknown Room')
        room_info = f"{numberofroom} * {room_name}"
        room_and_hotel_info_lines.append(room_info)

    # 添加酒店名称
    hotel_name = order_info.get('hotelName', 'Unknown Hotel')
    room_and_hotel_info_lines.append(hotel_name)

    # 确保列表中没有 None 元素，将 None 转换为 ''
    room_and_hotel_info_lines = [item if item is not None else '' for item in room_and_hotel_info_lines]

    # 使用"\n"连接所有房间和酒店信息行来创建最终的room_and_hotel_info文本
    room_and_hotel_info_text = "\n".join(room_and_hotel_info_lines)
        # 初始化 formatted_text_lines 列表来构建格式化的文本
    formatted_text_lines = [
        f"{order_state}",
        "ーーーーーーーーーーーーーーーーーーーーーーーーーー",
        f"ZYX Travel 予約番号 {order_info['orderNo']}  {get_agent_name(order_info['agentPurchaserCode'])}予約番号：{order_info['outOrderNo']}",
        "ーーーーーーーーーーーーーーーーーーーーーーーーーー",			
        f"{get_agent_name(order_info['agentPurchaserCode'])}予約番号：{order_info['outOrderNo']}",		
        f"ZYX予約番号：{order_info['orderNo']}",					
        f"チェックイン日：{order_info['checkIn']}  {days_difference} night(s)",
        f"チェックアウト : {order_info['checkOut']}",						
        "ホテル・ルーム情報：",
        room_and_hotel_info_text
    ]

    # 供应商信息
    formatted_text_lines.append("ーーーーーーーーーーーーーーーーーーーーーーーーーー")

    if 'orderCheckRecord' in order_info and isinstance(order_info['orderCheckRecord'], dict):
        zyx_order_no = order_info['orderCheckRecord'].get('zyxOrderNo', 'None')
        sub_order_no = order_info['orderCheckRecord'].get('supOrderNo', 'None')
        supplier_name = order_info.get('supplierName', 'Unknown Supplier')
        
        if order_info.get('supplierCode') == 'M122031275':
            supplier_section = [
                f"ZYX Travel 예약번호 {zyx_order_no}  {supplier_name} 예약번호 : {sub_order_no}",
                "ーーーーーーーーーーーーーーーーーーーーーーーーーー",	
                f"{supplier_name} 예약번호 : {sub_order_no}",
                f"ZYX Travel 예약번호 {zyx_order_no}",
                f"체크인 ：{order_info.get('checkIn', 'Unknown CheckIn')}   {days_difference} night(s)",
                f"체크아웃 : {order_info.get('checkOut', 'Unknown CheckOut')}",
                f"호텔 & 룸정보：",      
            ]
        else:
            supplier_section = [
                f"ZYX Travel 予約番号 {zyx_order_no}  {supplier_name} 予約番号 : {sub_order_no}",
                "ーーーーーーーーーーーーーーーーーーーーーーーーーー",	
                f"{supplier_name} 予約番号 : {sub_order_no}",
                f"ZYX Travel 予約番号 {zyx_order_no}",
                f"チェックイン日 ：{order_info.get('checkIn', 'Unknown CheckIn')}  {days_difference} night(s)",
                f"チェックアウト : {order_info.get('checkOut', 'Unknown CheckOut')}",
                f"ホテル・ルーム情報:",
            ]
        formatted_text_lines.extend(supplier_section)
        formatted_text_lines.append(room_and_hotel_info_text)
        formatted_text_lines.append("ーーーーーーーーーーーーーーーーーーーーーーーーーー")
    else:
        formatted_text_lines.append("\n None Supplier information\n")

    # 添加comments部分
    if 'comments' in order_info:
        formatted_text_lines.append("\nComments:")
        for comment in order_info['comments']:
            formatted_text_lines.append(f"    - {comment}")
    
    # 最后，将所有文本行连接起来
    # 确保所有项都是字符串，将 None 转换为空字符串
    formatted_text_lines = [str(item) if item is not None else '' for item in formatted_text_lines]
    formatted_text = "\n".join(formatted_text_lines)
    return formatted_text


# English
def format_order_s2(order_info):
    print(f"order_JP 函数 原本订单信息: {order_info}")
    days_difference = calculate_days_between_dates(order_info['checkIn'], order_info['checkOut'])

    order_state = get_order_status_description(order_info['orderStatus'])

    # 准备房型和酒店信息
    room_and_hotel_info_lines = []

    # 检查bookingDetails是否存在且是列表类型
    numberofroom = 0
    if order_info['bookingDetails'] and isinstance(order_info['bookingDetails'], list):
        numberofroom = order_info['bookingDetails'][0].get('numberOfRooms', 0)

    # 遍历orderProductDetails列表
    for product in order_info.get('orderProductDetails', []):
        room = product.get('room', {})
        room_name = room.get('name', 'Unknown Room')
        room_info = f"{numberofroom} * {room_name}"
        room_and_hotel_info_lines.append(room_info)

    # 添加酒店名称
    hotel_name = order_info.get('hotelName', 'Unknown Hotel')
    room_and_hotel_info_lines.append(hotel_name)

    # 确保列表中没有 None 元素，将 None 转换为 ''
    room_and_hotel_info_lines = [item if item is not None else '' for item in room_and_hotel_info_lines]

    # 使用"\n"连接所有房间和酒店信息行来创建最终的room_and_hotel_info文本
    room_and_hotel_info_text = "\n".join(room_and_hotel_info_lines)
        # 初始化 formatted_text_lines 列表来构建格式化的文本
    formatted_text_lines = [
        f"{order_state}",
        "ーーーーーーーーーーーーーーーーーーーーーーーーーー",
        f"ZYX Travel Order No {order_info['orderNo']}  {get_agent_name(order_info['agentPurchaserCode'])} Order No：{order_info['outOrderNo']}",
        "ーーーーーーーーーーーーーーーーーーーーーーーーーー",			
        f"{get_agent_name(order_info['agentPurchaserCode'])}Order No：{order_info['outOrderNo']}",		
        f"ZYX Travel Order No：{order_info['orderNo']}",					
        f"Check In：{order_info['checkIn']}  {days_difference} night(s)",
        f"Check Out : {order_info['checkOut']}",						
        "Hotel & Rooms Information",
        room_and_hotel_info_text
    ]

    # 供应商信息
    formatted_text_lines.append("ーーーーーーーーーーーーーーーーーーーーーーーーーー")

    if 'orderCheckRecord' in order_info and isinstance(order_info['orderCheckRecord'], dict):
        zyx_order_no = order_info['orderCheckRecord'].get('zyxOrderNo', 'None')
        sub_order_no = order_info['orderCheckRecord'].get('supOrderNo', 'None')
        supplier_name = order_info.get('supplierName', 'Unknown Supplier')
        
        if order_info.get('supplierCode') == 'M122031275':
            supplier_section = [
                f"ZYX Travel Order No {zyx_order_no}  {supplier_name} Order No：{sub_order_no}",
                "ーーーーーーーーーーーーーーーーーーーーーーーーーー",	
                f"{supplier_name} Order No：{sub_order_no}",
                f"ZYX Travel Order No {zyx_order_no}",
                f"Check In ：{order_info.get('checkIn', 'Unknown CheckIn')}   {days_difference} night(s)",
                f"Check Out ：{order_info.get('checkOut', 'Unknown CheckOut')}",
                f"Hotel & Rooms Information :",      
            ]
        else:
            supplier_section = [
                f"ZYX Travel Order No : {zyx_order_no}  {supplier_name} Order No：{sub_order_no}",
                "ーーーーーーーーーーーーーーーーーーーーーーーーーー",	
                f"{supplier_name} Order No：{sub_order_no}",
                f"ZYX Travel Order No : {zyx_order_no}",
                f"Check In ：{order_info.get('checkIn', 'Unknown CheckIn')}  {days_difference} night(s)",
                f"Check Out ：{order_info.get('checkOut', 'Unknown CheckOut')}",
                f"Hotel & Rooms Information :",
            ]
        formatted_text_lines.extend(supplier_section)
        formatted_text_lines.append(room_and_hotel_info_text)
        formatted_text_lines.append("ーーーーーーーーーーーーーーーーーーーーーーーーーー")
    else:
        formatted_text_lines.append("\n None Supplier information\n")

    # 添加comments部分
    if 'comments' in order_info:
        formatted_text_lines.append("\nComments:")
        for comment in order_info['comments']:
            formatted_text_lines.append(f"    - {comment}")
    
    # 最后，将所有文本行连接起来
    # 确保所有项都是字符串，将 None 转换为空字符串
    formatted_text_lines = [str(item) if item is not None else '' for item in formatted_text_lines]
    formatted_text = "\n".join(formatted_text_lines)
    return formatted_text




def format_order_kr(order_info):
    formatted_text = f"""
    ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    {order_info['orderNo']} 　야놀자 예약번호 {order_info['orderCheckRecord'].get('supOrderNo','None')} 
    ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー			
    야놀자 예약번호: {order_info['orderCheckRecord'].get('supOrderNo','None')} 	
    ZYX　예약번호 : {order_info['orderNo']} 					
    입주날자 :{order_info['checkIn']}  
    체크아웃 :{order_info['checkOut']} 
    호텔 &룸 정보 ：
    """
    for product in order_info['orderProductDetails']:
        room = product['room']
        formatted_text += f"Room Name: {room['name']}\n" 
    formatted_text += f"""
    Hotel Name: {order_info['hotelName']}
    """
    return formatted_text

def format_order_en(order_info):
    return 
def format_order_cn(order_info):
    return 
def format_order_all(order_info):
    return


# 获得所有信息
def format_order_info_all(order_info):
    # 将None值转换为人类可读的形式
    def format_value(value):
        if value is None:
            return 'None'
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        return value
    
    # 格式化日期时间
    def format_datetime(dt_string):
        try:
            return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        except ValueError:
            try:
                return datetime.strptime(dt_string, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                return dt_string  # 如果都不匹配，返回原始字符串
    
    # 格式化列表内容
    def format_list(lst):
        return json.dumps(lst, ensure_ascii=False, indent=4)
    
    # 开始构建格式化文本
    formatted_text = [
        "Order Information Overview:",
        f"h Code: {format_value(order_info.get('code'))}",
        f"Message: {format_value(order_info.get('message'))}",
        f"Hotel Code: {format_value(order_info.get('hotelCode'))}",
        f"Order Number: {format_value(order_info.get('orderNo'))}",
        f"Hotel Name: {format_value(order_info.get('hotelName'))}",
        f"Check-In Date: {format_datetime(order_info.get('checkIn'))}",
        f"Check-Out Date: {format_datetime(order_info.get('checkOut'))}",
        f"Total Price: {format_value(order_info.get('totalPrice'))} {format_value(order_info.get('currencyCode'))}",
        f"Contact Name: {format_value(order_info.get('contactsName'))}",
        f"Contact Phone: {format_value(order_info.get('contactsPhone'))}",
        f"Contact Email: {format_value(order_info.get('contactsEmail'))}",
        f"Remarks: {format_value(order_info.get('remarks'))}",
        f"Order Status: {format_value(order_info.get('orderStatus'))}",
        f"Last Cancel Date: {format_datetime(order_info.get('lastCancelDate'))}",
        f"Canceled: {format_value(order_info.get('canceled'))}",
        "Booking Details: " + format_list(order_info.get('bookingDetails', [])),
        "Order Product Details: " + format_list(order_info.get('orderProductDetails', [])),
        "Order Refund Details: " + format_list(order_info.get('orderRefundDetails', [])),
        "Order Check Record: " + format_list([order_info.get('orderCheckRecord', {})]),
        f"Exchange Rate: {format_value(order_info.get('exchangeRate'))}",
    ]
    
    # 将列表中的每个元素用换行符连接
    return "\n".join(formatted_text)

def handle_order_number2(zyx_order, param):
    print("进入了 handle_order_number")
    # 基本URL
    base_url = "https://disapi.zyxtravel.com/in-service/api/order/detail"
    # zyx_order = "ZY2403292530"
    # 请求参数，转换为JSON字符串并进行URL编码
    params = json.dumps({"partnerCode": "M0001", "orderNo": f"{zyx_order}"})
    encoded_params = requests.utils.quote(params)
    
    # 构造完整的URL
    url = f"{base_url}?json={encoded_params}"
    # print(f"Fetching order details for: {zyx_order}")
    # print(url)
    
    # 发送GET请求（假设API通过查询参数接收JSON数据）
    response = requests.post(url)  # 注意：这里没有传递json=data，因为我们已经将数据作为URL的一部分

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析响应的JSON数据
        order_info = response.json()
        #print("order_info 原始信息 ：", order_info)
         # 参数分析
        print("param-text : ", param)
        if param == "none":
            order_info = format_order_s(order_info)
        elif param == "S":
            order_info = format_order_s2(order_info)
        elif param == "A":
            order_info = format_order_info_all(order_info)
        return order_info
    else:
        print("请求失败，状态码:", response.status_code, "响应内容:", response.text)

# 副本
def handle_order_number(zyx_order, param):
    print("进入了 handle_order_number")

   # 基本URL
    base_url = "https://disapi.zyxtravel.com/in-service/api/order/detail"
    # zyx_order = "ZY2403292530"
    # 请求参数，转换为JSON字符串并进行URL编码
    params = json.dumps({"partnerCode": "M0001", "orderNo": f"{zyx_order}"})
    encoded_params = requests.utils.quote(params)
    
    # 构造完整的URL
    url = f"{base_url}?json={encoded_params}"
    print(f"Fetching order details for: {zyx_order}")
    print(url)
    
    # 发送GET请求（假设API通过查询参数接收JSON数据）
    response = requests.post(url)  # 注意：这里没有传递json=data，因为我们已经将数据作为URL的一部分

    if response.status_code == 200:
        order_info = response.json()
        print(f"处理参数: {param.lower()}")  # 处理参数前转换为小写
        if param.lower() == "none":
            print("进入了 None")
            order_info = format_order_s(order_info)
        elif param.lower() == "s":
            print("进入了 S")
            order_info = format_order_s2(order_info)
        elif param.lower() == "a":
            print("进入了 a")
            order_info = format_order_info_all(order_info)
        return order_info
    else:
        error_message = f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}"
        print(error_message)
        return error_message  # 返回错误信息

