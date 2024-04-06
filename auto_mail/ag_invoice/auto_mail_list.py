import base64
import csv
from datetime import datetime, timezone, timedelta
from email import policy, message_from_bytes
import html
from io import BytesIO
import os
import pickle

from bs4 import BeautifulSoup, Comment
from googleapiclient.discovery import build
from google.cloud import translate_v2 as translate
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from openpyxl import load_workbook

# 本地文件导入
# from zyx_slack import send_slack_message  # 如果你使用Slack发送消息的功能
from get_zyx_order import handle_order_number
from lod_xlsx import create_xlsx_file  # 这里有个小错误，在文件名中
from get_service import getService # 邮件 getService
from send_gmail import agoda_invoice # 发送 agoda invoice 邮件

# print("Current working directory:", os.getcwd())
# 如果修改了 SCOPES，删除 token.pickle 文件。
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

# 确保导入和初始化translate.Client()
translate_client = translate.Client()

# 获得所有条件下邮件函数，默认为全部，慎用！！！
def SearchMessages_all(service, user_id, query=''):
    try:
        messages = []
        response = service.users().messages().list(userId=user_id, q=query).execute()

        if 'messages' in response:
            messages.extend(response['messages'])

        # 使用nextPageToken循环获取所有邮件
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# 只获得邮件文本函数
def GetMessageContent(message):
    """解析MIME消息并提取文本内容。现在也能处理多部分消息。"""
    def decode_part(part):
        """解码邮件部分的辅助函数。"""
        part_bytes = base64.urlsafe_b64decode(part['body']['data'])
        return part_bytes.decode()

    # 检查是否为多部分消息
    if 'parts' in message['payload']:
        # 遍历所有部分，尝试找到文本或HTML内容
        for part in message['payload']['parts']:
            mime_type = part['mimeType']
            if mime_type == 'text/plain' or mime_type == 'text/html':
                return decode_part(part)
            # 对于嵌套的多部分，递归处理
            if 'parts' in part:
                nested_text = GetMessageContent({'payload': part})
                if nested_text:
                    return nested_text
    elif 'body' in message['payload'] and 'data' in message['payload']['body']:
        # 非多部分消息，直接解码并返回
        return decode_part(message['payload'])
    return "无法找到可提取的文本内容。"


# 去除 html格式 却保留原来格式显示
def clean_html(html_content):
    """去除HTML内容中的所有标签和注释，将<br>和<p>转换为换行符。"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 将<br>和<p>标签转换为换行符\n
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all("p"):
        p.append("\n")  # 在<p>标签的结束处添加换行符
        p.unwrap()  # 移除<p>标签但保留其内容

    # 移除HTML注释
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()

    # 使用get_text()去除剩余的HTML标签，保留纯文本
    text = soup.get_text()

    # 进一步清理文本，如去除连续的换行符
    cleaned_text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])

    return cleaned_text

#清理HTML，还有翻译
def clean_and_translate_html(html_content, target_language="zh-CN"):
    """去除HTML内容中的所有标签和注释，将<br>和<p>转换为换行符，然后翻译文本，保留原始换行格式。"""
    # 去除HTML并获取清理后的文本
    soup = BeautifulSoup(html_content, 'html.parser')
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for p in soup.find_all("p"):
        p.append("\n")
        p.unwrap()
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()
    text = soup.get_text(separator="\n")  # 保留换行符
    cleaned_text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])

    # 初始化翻译客户端
    translate_client = translate.Client()

    # 检测文本语言
    detected_language = translate_client.detect_language(cleaned_text)['language']
    if detected_language == 'en':
        # 如果是英文，进行翻译
        translation = translate_client.translate(cleaned_text, target_language=target_language)
        translated_text = translation['translatedText']
        # 解码HTML实体，保留换行
        translated_text = html.unescape(translated_text)
        return cleaned_text, translated_text
    else:
        # 如果不是英文，只返回原文
        return cleaned_text, None
# 示例调用
# clean_and_translate_html("<p>Hello, world!</p><br><p>This is a test.</p>", "zh-CN")

# 全部加上 几个特殊信息获取
def GetMessageDetails(service,user_id,msg_id):
    try:
        # 获取单个邮件的详细信息
        # print(f"这是 GetMessage Details 函数 : {msg_id}")  # 正确地使用变量
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()  # 直接使用msg_id变量
        # 获取并打印基础信息
        headers = message['payload']['headers']
        thread_id = message['threadId']
        for header in headers:
            if header['name'] == 'From':
                print("From:", header['value'])
            elif header['name'] == 'Subject':
                print("Subject:", header['value'])
            elif header['name'] == 'Date':
                print("Date:", header['value'])  # 这是邮件被发送的时间
        
        # 获取对话信息来确定邮件数量和第一次到达时间
        thread = service.users().threads().get(userId=user_id, id=thread_id, format='full').execute()
        messages = thread['messages']
        print("Messages in thread:", len(messages))

        # 格式化时间戳
        first_message_timestamp = int(messages[0]['internalDate']) / 1000  # Gmail API的时间戳是毫秒
        last_message_timestamp = int(messages[-1]['internalDate']) / 1000
        jst = timezone(timedelta(hours=+9))  # 日本时间
        first_message_date = datetime.fromtimestamp(first_message_timestamp, jst).strftime('%Y年%m月%d日 %H:%M:%S')
        last_message_date = datetime.fromtimestamp(last_message_timestamp, jst).strftime('%Y年%m月%d日 %H:%M:%S')
        print(f"First message timestamp: {first_message_date}")
        print(f"Last message timestamp: {last_message_date}")

        # 判断最后一条消息是发送还是接收的，并打印发件人
        last_msg_headers = messages[-1]['payload']['headers']
        last_msg_from = next(header['value'] for header in last_msg_headers if header['name'] == 'From')
        print("Last message was", "received from" if "zyxcs001@gmail.com" in last_msg_from else "sent to", last_msg_from)

        # 解析邮件内容
        payload = message['payload']
        if 'parts' in payload:
            # 如果邮件有多个部分，处理第一个部分（通常是正文）
            part_body = payload['parts'][0]['body']['data']
        else:
            # 如果邮件没有多个部分，直接获取正文
            part_body = payload['body']['data']
        text = base64.urlsafe_b64decode(part_body).decode('utf-8')
        #清除HTML
        # cleaned_text = clean_html(text)
        cleaned_text = clean_and_translate_html(text, "zh-CN")
        # 获取特定部分的内容
        start_phrase = "お世話になります"
        end_phrase = "よろしくお願い申し上げます。"
        start_index = cleaned_text.find(start_phrase)
        end_index = cleaned_text.find(end_phrase)
        if start_index != -1 and end_index != -1:
            specific_content = cleaned_text[start_index:end_index + len(end_phrase)]
            print("Specific content:", specific_content)
        else:
            print("Specific content not found.")
            
    except Exception as error:
        print(f'An error occurred with message ID {msg_id}:', error)
        print('An error occurred:', error)

# 获得标签信息
def ListLabels(service, user_id):
    try:
        response = service.users().labels().list(userId=user_id).execute()
        labels = response.get('labels', [])
        for label in labels:
            print(f"Label ID: {label['id']}, Label Name: {label['name']}")
    except Exception as e:
        print(f"An error occurred: {e}")

def ListMessages(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])
        return messages
    except Exception as error:
        print('An error occurred: %s' % error)

# 一般信息
def GetMessage(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        payload = message['payload']
        headers = payload.get("headers")
        parts = payload.get("parts")
        for header in headers:
            if header['name'] == 'From':
                print("From: ", header['value'])
            if header['name'] == 'Subject':
                print("Subject: ", header['value'])
                # GetMessageDetails(service, 'me', msg_id)
        if parts:
            part_body = parts[0]['body']
            data = part_body['data']
            text = base64.urlsafe_b64decode(data).decode()
            print("Body: ", text[:100])  # 打印前100个字符作为预览
    except Exception as error:
        print('An error occurred: %s' % error)

# 先查询邮件再下载
def SearchMessages(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        return response.get('messages', [])
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
# 相关所有邮件获取
def GetThreadMessages(service, user_id, thread_id):
    """获取并返回指定线索ID的所有邮件"""
    try:
        thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
        return thread['messages']
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

#获得邮件头部分信息
def get_header(message, header_name):
    """从邮件的payload中提取指定名称的头信息"""
    headers = message['payload'].get('headers', [])
    for header in headers:
        if header.get('name') == header_name:
            return header.get('value')
    return None


# 添加邮件属性：新邮件，之前邮件
def print_email_info(service, user_id, message, thread_messages_count):
    # 提取邮件头信息
    headers = message['payload']['headers']
    subject = [header['value'] for header in headers if header['name'] == 'Subject'][0]
    date = [header['value'] for header in headers if header['name'] == 'Date'][0]

    # 检查是否为新邮件
    if 'UNREAD' in message['labelIds']:
        mail_status = "※※※※※※※※※※※※※※※※※※※※ New mail ※※※※※※※※※※※※※※※※※※※※"
    else:
        mail_status = f"※※※※※※※※※※※※※※※※※※※※ Re mail ※※※※※※※※※※※※※※※※※※※※ [{thread_messages_count} mail]"

    print(mail_status)
    print(f"Date: {date}")
    print(f"Subject: {subject}")

# 下载文件
def download_attachment(service, user_id, msg_id, attachment_id):
    try:
        attachment = service.users().messages().attachments().get(userId=user_id, messageId=msg_id, id=attachment_id).execute()
        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
        
        # 定义文件保存路径
        file_path = (f"down_file/down_file_{msg_id}.csv")
        with open(file_path, "wb") as f:
            f.write(file_data)      
        print(f"File saved to {file_path}")
        
        # 尝试读取保存的CSV文件,需要读取保存文件时，再打开。
        '''
        try:
            with open(file_path, mode='r', encoding='utf-16') as file:
                reader = csv.DictReader(file, delimiter='\t')
                for row in reader:
                    # 确保CSV文件中有这些列名
                    print ("下载文件内容确认部分:")
                    print(row['First Name'], row['Last Name'], row['E-mail'], "...?...", row.get('Booking External Reference', 'N/A'))
        except Exception as e:
            print(f"Error reading CSV file X: {e}")
        '''
        return file_path  # 返回文件路径
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# 获取第一个附件的ID
def get_first_attachment_id(service, user_id, msg_id):
    """获取邮件中第一个附件的ID"""
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        parts = message['payload']['parts']
        for part in parts:
            if part['filename']:  # 有文件名的部分是附件
                attachment_id = part['body']['attachmentId']
                return attachment_id
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

# 读取下载的文件函数
def parse_csv_file(file_path):
    created_files = []  # 初始化一个列表来收集文件路径
    try:
        with open(file_path, mode='r', encoding='utf-16') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                zyx_order_info = handle_order_number(row['Booking External Reference'], is_format=False)
                # 创建xlsx文件，并接收返回的文件路径
                file_path = create_xlsx_file(row, zyx_order_info)
                if file_path:  # 确保路径非空
                    created_files.append(file_path)  # 收集文件路径
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return created_files  # 返回收集到的所有文件路径

# 主函数  
def main():
    service = getService()
    # query = ''  # 全部邮件
    # query = 'subject:ZY2403121983'
    # query = 'Invoice request'
    query = 'from:CSI.invoices@agoda.com subject:"Invoice request"'
    messages = SearchMessages(service, 'me', query)
    if not messages:
        print("No messages found.")
        return

    print(f"Found {len(messages)} messages.")
    thread_ids_seen = set() 

    for message in messages[:1]:  # 处理前5个邮件
        thread_id = message['threadId']
        if thread_id in thread_ids_seen:
            continue
        thread_ids_seen.add(thread_id)
        msg_id = message['id']
        # 获取每封邮件的完整信息
        full_message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()  
        thread_messages = GetThreadMessages(service, 'me', thread_id)
        # print_email_info(service, 'me', message, len(thread_messages))  # 打印邮件信息
        # 现在可以安全地调用print_email_info，因为我们已经获取了完整的邮件对象
        # 获取该线索中所有邮件的数量，需要获取线索详情
        thread_id = full_message['threadId']
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        thread_messages_count = len(thread['messages'])

        # 附件相关部分
        print(f'Processing message ID: {msg_id}')
        # 获取第一个附件的ID
        attachment_id = get_first_attachment_id(service, user_id='me', msg_id=msg_id)
        if attachment_id:
            # print(f'Found attachment ID: {attachment_id}')
            
            # 下载附件
            file_data = download_attachment(service, user_id='me', msg_id=msg_id, attachment_id=attachment_id)
            
            if file_data:
                print('Attachment downloaded successfully.')
                # 这里你可以添加处理下载文件数据的代码
                # 分析数据
                # 就是因为这么调用，创建了2次文件，以后注意！！！！
                # parse_csv_file(file_data)
                # 假设`file_path`是你的CSV文件路径
                created_files = parse_csv_file(file_data)
                if created_files:  # 如果有创建的文件
                    agoda_invoice(created_files)  # 调用函数发送邮件
                else:
                    print("No files were created.")
            else:
                print('No file data.')
        else:
            print('No attachment found.')

        print_email_info(service, 'me', full_message, thread_messages_count)
        print("╭╮╭╮╭╮╭╮╭╮╭╮╭╮ START One MAIL ╭╮╭╮╭╮╭╮╭╮╭╮╭╮")
        print(f"msg_id : {msg_id}")
        for msg in thread_messages:
            # 获取邮件时间、标题、发件人和收件人信息
            date = get_header(msg, 'Date')
            subject = get_header(msg, 'Subject')
            from_header = get_header(msg, 'From')
            to_header = get_header(msg, 'To')

            # 提取邮件内容
            msg_content = GetMessageContent(msg)
            original_text, translated_text = clean_and_translate_html(msg_content)

            # 打印邮件信息
            print("------------------- start re mail -------------------")
            print(f"Date: {date}")
            print(f"Subject: {subject}")
            print(f"From: {from_header}")
            print(f"To: {to_header}")
            print(f"Mail Contents:\n{original_text}")
            if translated_text:
                print(f"检测到英文，翻译成中文 : \n{translated_text}")  # 只有当检测到英文时才打印翻译
            # send_slack_message(f"Date:{date}\n Subject: {subject} \n From:{from_header} \n To:{to_header}")
            print("------------------- end re mail -------------------")    
    print("╰╯╰╯╰╯╰╯╰╯╰╯╰╯ END One MAIL ╰╯╰╯╰╯╰╯╰╯╰╯╰╯")
if __name__ == '__main__':
    main()