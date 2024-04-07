import requests
import json
from datetime import datetime
'''
ZY2401136103  AGODA予約番号：1119246684
ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー			
agoda予約番号：1119246684		
ZYX予約番号：ZY2401136103					
チェックイン日：2024-01-28   2 night(s)						
ホテル情報：
1 * Premier terrace Room
[济州岛] Jeju the nine stay
ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー	
ZY2401271823　야놀자 예약번호 2401271367185240
ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー			
야놀자 예약번호: 2401260767050882	
ZYX　예약번호 : ZY2401271894					
입주 날자 ：2024-01-27  1 night(s)						
호텔 &룸 정보 ：
"1 * Deluxe Queen Room
[西归浦] Jeju Seogwipo HI Hotel (HI)
ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
'''

def format_jp(order_info):
    # print(f"原本订单信息: {order_info}")
    formatted_text = f"""
        ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    ZYX Travel 予約番号 {order_info['orderNo']}  
    agoda予約番号：{order_info['outOrderNo']}
    ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー			
    agoda予約番号：{order_info['outOrderNo']}		
    ZYX予約番号：{order_info['orderNo']} 					
    チェックイン日：{order_info['checkIn']}   
    チェックアウト : {order_info['checkOut']}						
    ホテル情報：
    """
    for product in order_info['orderProductDetails']:
        room = product['room']
        formatted_text += f"Room Name: {room['name']}\n" 
    formatted_text += f"""
    Hotel Name: {order_info['hotelName']}
    """
    return formatted_text

def format_kr(order_info):
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
            return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S").strftime("%Y年%m月%d日 %H:%M")
        except ValueError:
            # 如果不是完整的日期时间格式，尝试只处理日期
            try:
                return datetime.strptime(dt_string, "%Y-%m-%d").strftime("%Y年%m月%d日")
            except ValueError:
                return dt_string  # 如果都不匹配，返回原始字符串

    formatted_text = "Order Info:\n"
    for key, value in order_info.items():
        if key in ['checkIn', 'checkOut', 'lastCancelDate', 'cancelDate']:
            value = format_datetime(value)
        elif isinstance(value, list):
            value = json.dumps(value, ensure_ascii=False, indent=2)  # 以JSON格式美化列表
        else:
            value = format_value(value)
        formatted_text += f"- {key}: {value}\n"

    return formatted_text


def format_order_info(order_info):
    # 格式化基本信息
    formatted_text = f"""
Order Information Overview:
Order Number: {order_info['orderNo']}
Hotel Code: {order_info['hotelCode']}
Hotel Name: {order_info['hotelName']}
Check-in Date: {order_info['checkIn']}
Check-out Date: {order_info['checkOut']}
Total Price: {order_info['totalPrice']} {order_info['currencyCode']}
Remarks: {order_info['remarks']}
Cancellation Allowed Until: {order_info['lastCancelDate']}
Cancelled: {"Yes" if order_info['canceled'] else "No"}

Booking Details:
"""
    # 格式化预订详情
    for detail in order_info['bookingDetails']:
        formatted_text += f"  - Product Code: {detail['productCode']}, Rooms: {detail['numberOfRooms']}, Meal Type: {detail['mealType']}, Guest Type: {detail['guestType']}\n"
        for customer_info in detail['customerInfos']:
            formatted_text += f"    Adults: {customer_info['numberOfAdults']}, Children: {customer_info['numberOfChildren']}\n"
    
    # 格式化房间详情
    formatted_text += "\nRoom Details:\n"
    for product in order_info['orderProductDetails']:
        room = product['room']
        formatted_text += f"  - Room Name: {room['name']}, WiFi: {'Yes' if room['wifi'] == '1' else 'No'}, Bed Type: {', '.join([bed['code'] for bed in room['bedType']['beds']])}\n"
    
    # 格式化退款详情
    formatted_text += "\nRefund Details:\n"
    if 'orderRefundDetails' in order_info and order_info['orderRefundDetails']:
        for refund in order_info['orderRefundDetails']:
            formatted_text += f"  - Refund Type: {refund['refundType']}, Value: {refund['refundValue']}, Cancel Date: {refund['cancelDate']}\n"
        pass
    else:
        # 没有找到orderRefundDetails或者它是None
        print("No refund details found or it's None")
        
    
    # 格式化订单核对记录
    check_record = order_info['orderCheckRecord']
    formatted_text += f"""
Order Check Record:
- ZYX Order No: {check_record['zyxOrderNo']}
- Hotel Code: {check_record['zyxHotelCode']}
- Partner Room Code: {check_record['zyxPartnerRoomCode']}
- Product Code: {check_record['zyxProductCode']}
- Hotel Name (EN): {check_record['zyxHotelNameEn']}
- Room Name (EN): {check_record['zyxRoomtypeNameEn']}
- Smoking Policy: {'Smoking' if check_record['zyxSmokingPolicy'] == '1' else 'Non-Smoking'}
- Meal Policy: {check_record.get('zyxMealPolicy', 'N/A')}
- Cancellation Policy: {check_record['zyxCancelPolicy']}
"""
    return formatted_text

# 调用函数并打印结果
# print(format_order_info(order_info))

def handle_order_number(zyx_order):
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
        #print("原本订单信息:", order_info)
        order_info = format_order_info_all(order_info)
        return order_info
    else:
        print("请求失败，状态码:", response.status_code, "响应内容:", response.text)

''' 备用参数 
- 联系人姓名: {order_info['contactsName']}
- 联系电话: {order_info['contactsPhone']}
- 联系邮箱: {order_info['contactsEmail']}
# Contact Name: {order_info['contactsName']}
'''

# 使用示例
# print(format_order_info(order_info))
