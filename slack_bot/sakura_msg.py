import requests

def send_message_to_channel(channel_id, message_text, token):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'channel': channel_id, 'text': message_text}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and response.json().get('ok'):
        print("Message sent successfully.")
    else:
        print(f"Failed to send message: {response.text}")

# 示例值，需替换为实际的频道ID和bot的OAuth Access Token
slack_channel_id = 'C06BK41ACJE'  # 替换为目标频道的ID
slack_bot_token = 'xoxb-6386497298406-6893488517924-2xJYTLFsz3bWRk8POiznWcyl'
# message = "[ZY予約番号 s] このように入力してみてください! ^^ "
message = "個人チャットができますので、必要な方は私に個人でこのように送ってください。"
# message = "はい！いまからです！　日本語、中国語、韓国語、英語。明日には全部可能です。少々お待ちください。"

send_message_to_channel(slack_channel_id, message, slack_bot_token)
