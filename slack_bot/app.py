from flask import Flask, request, jsonify
import requests  # 确保导入了requests库
from get_zyx_order import handle_order_number
import logging
import re

logging.basicConfig(level=logging.INFO)

# 然后，使用logging来代替print
app = Flask(__name__)

# Slack Bot的OAuth访问令牌
slack_token = 'xoxb-6386497298406-6893488517924-2xJYTLFsz3bWRk8POiznWcyl'


# 定义正则表达式
# 严格匹配 "ZY" 后跟 10 位数字，可能的空格，和可选的单个字符参数 'a' 或 's'
order_number_pattern_strict = re.compile(r'(?i)^ZY\d{10}$')

order_number_with_param_pattern = re.compile(r'(?i)^ZY\d{10}\s+[as]$')


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    if 'event' in data:
        event = data['event']
        if event.get('type') == 'message' and 'subtype' not in event:
            text = event.get('text').strip()  # 清理前后空白
            channel_id = event.get('channel')

            # 尝试匹配严格的订单号
            strict_match = order_number_pattern_strict.match(text)
            param_match = order_number_with_param_pattern.match(text)

            if strict_match:
                # 仅订单号逻辑
                response_text = handle_order_number(strict_match.group(), "none")
            elif param_match:
                # 订单号 + 参数逻辑
                order_number, param = param_match.group().split()
                response_text = handle_order_number(order_number, param)
            else:
                return jsonify({'status': 'No valid order number'})

            # 发送消息到 Slack
            send_message_to_slack(channel_id, response_text)

    return jsonify({'status': 'OK'})

def send_message_to_slack(channel_id, message_text):
    # print(f"Sending message: {message_text} to channel {channel_id}")
    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': 'Bearer ' + slack_token}
    data = {'channel': channel_id, 'text': message_text}
    response = requests.post(url, headers=headers, json=data)
    # logging.info("Received Slack event: %s", data)
    # print("Slack response:", response.json())  # 打印Slack API的响应
    if not response.ok:
        print("Error sending message:", response.text)

if __name__ == "__main__":
    app.run(debug=True, port=3000)  # 确保和ngrok的端口一致

