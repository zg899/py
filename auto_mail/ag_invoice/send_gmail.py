from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
import os

import mimetypes
from googleapiclient.errors import HttpError

from get_service import getService

# 转换文件名称
service = getService()

def create_message_with_attachment(sender, to, subject, message_text, cc=None, files=[]):
    """
    创建一封包含多个附件的邮件。
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    # 添加Cc字段
    if cc:
        message['Cc'] = cc

    msg = MIMEText(message_text)
    message.attach(msg)
    
    for file in files:
        content_type, encoding = mimetypes.guess_type(file)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'rb')
            msg = MIMEText(fp.read().decode(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            fp.close()
        
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
    
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:  # 注意这里的修改
        print('An error occurred: %s' % error)


# 使用示例
# 假设你已经有了一个名为`service`的Gmail API服务实例
def agoda_invoice(files):
    sender = "zyxcs001@gmail.com"
    to = "csi.invoices@agoda.com"
    #to = "noa.jung@gmail.com"
    #cc = "g@zhiyuanxing.com"
    cc = "fong@zyxtravel.com, g@zhiyuanxing.com, PS-3PS@agoda.com"  # 抄送给多个收件人
    subject = "Reply to Invoice request - From ZYXTRAVEL"
    message_text = "Hello,\nThis is ZYXTRAVEL.\nThe attachment is the invoice you want, please confirm.\nHave a nice day.\n\n"
    # print(files)
    message = create_message_with_attachment(sender, to, subject, message_text, cc, files)
    send_message(service, "me", message)
    print("邮件发送完毕!")

