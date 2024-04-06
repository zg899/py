import requests
import json

def format_order_info(order_info):
    formatted_text = f"""
订单信息概览:
- 订单号: {order_info['orderNo']}
- 酒店代码: {order_info['hotelCode']}
- 酒店名称: {order_info['hotelName']}
- 入住日期: {order_info['checkIn']}
- 退房日期: {order_info['checkOut']}
- 总价格: {order_info['totalPrice']} {order_info['currencyCode']}
- 外部订单号: {order_info['outOrderNo']}
- 最后取消日期: {order_info['lastCancelDate']}
- 取消状态: {"是" if order_info['canceled'] else "否"}
- 订单状态: {order_info['orderStatus']}
- 房间类型: {order_info['orderProductDetails'][0]['room']['name']}
- 房间数量: {order_info['bookingDetails'][0]['numberOfRooms']}
- 餐食类型: {order_info['bookingDetails'][0]['mealType']}
- 客人类型: {order_info['bookingDetails'][0]['guestType']}
- 成人数量: {order_info['bookingDetails'][0]['customerInfos'][0]['numberOfAdults']}
- 儿童数量: {order_info['bookingDetails'][0]['customerInfos'][0]['numberOfChildren']}
- 客人信息: 姓名 {order_info['bookingDetails'][0]['customerInfos'][0]['customers'][0]['firstName']} {order_info['bookingDetails'][0]['customerInfos'][0]['customers'][0]['lastName']}, 国籍 {order_info['bookingDetails'][0]['customerInfos'][0]['customers'][0]['nationality']}

订单详情:
"""
    for product in order_info['orderProductDetails']:
        formatted_text += f"- 产品代码: {product['productCode']}\n"
        formatted_text += f"- 产品名称: {product['productName']}\n"
        for plan in product['ratePlans']:
            formatted_text += f"- 入住日期: {plan['saleDate']}, 价格: {plan['prices']}\n"
    return formatted_text.strip()


def handle_order_number(zyx_order,is_format = True):
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
        print("订单信息:", order_info)
        if is_format == True:
            order_info = format_order_info(order_info)
        return order_info
    else:
        print("请求失败，状态码:", response.status_code, "响应内容:", response.text)

''' 备用参数 
- 联系人姓名: {order_info['contactsName']}
- 联系电话: {order_info['contactsPhone']}
- 联系邮箱: {order_info['contactsEmail']}
'''
# 使用示例
# print(format_order_info(order_info))
