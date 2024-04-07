from flask import Flask, request, jsonify
import requests  # 导入requests库用于发送HTTP请求

app = Flask(__name__)

# 假设这是你的订单信息API的URL和请求头
ORDER_INFO_API_URL = "https://disapi.zyxtravel.com/in-service/api/order/detail"
ORDER_INFO_API_HEADERS = {
    "Content-Type": "application/json",
    # 如果需要的话，添加其他必要的头部信息
}

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})
    
    # 处理Slack消息事件
    if data['event']['type'] == 'message' and 'text' in data['event']:
        message_text = data['event']['text']
        
        # 解析消息文本以提取订单号和语言代码，以下仅为示例
        # 假设消息文本格式为“order: 订单号 language: 语言代码”
        try:
            order_no, lang_code = parse_message_text(message_text)  # 你需要实现这个函数
            
            # 根据订单号和语言代码构建请求API
            order_info_response = requests.post(ORDER_INFO_API_URL, headers=ORDER_INFO_API_HEADERS, json={
                "partnerCode": "M0001",
                "orderNo": order_no,
            })
            order_info = order_info_response.json()
            
            # 处理API响应，发送结果回Slack
            send_order_info_to_slack(order_info, lang_code)  # 你需要实现这个函数
        except Exception as e:
            print(f"Error processing message: {e}")
        
    return jsonify({'status': 'OK'})

def parse_message_text(message_text):
    # 这里添加解析逻辑
    pass

def send_order_info_to_slack(order_info, lang_code):
    # 这里添加发送信息到Slack的逻辑
    pass

if __name__ == "__main__":
    app.run(debug=True, port=3000)  # 确保和ngrok的端口一致
