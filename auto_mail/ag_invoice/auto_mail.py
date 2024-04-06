from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
from email.mime.text import MIMEText

# 如果修改了 SCOPES，删除 token.pickle 文件。
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def getService():
    creds = None
    # token.pickle 存储了用户的访问和刷新令牌，首次运行时会自动创建
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # 如果没有有效的凭据，让用户登录。
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_330973435542-m8o1tqrlbjoq4n5d5uc9l1u568t0tr5e.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 保存凭据以备下次运行
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print('An error occurred: %s' % error)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def main():
    service = getService()
    sender = "webook001@gmail.com"
    to = "zyxcs001@gmail.com"
    subject = "Hello from Gmail API"
    message_text = "This is a test email."
    message = create_message(sender, to, subject, message_text)
    send_message(service, "me", message)

if __name__ == '__main__':
    main()
