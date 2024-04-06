from googleapiclient.discovery import build
from google.cloud import translate_v2 as translate
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
import os
import pickle

#基础服务信息
def getService():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                # echo 'export GOOGLE_APPLICATION_CREDENTIALS="/Users/2024/python/code/py/auto_mail/auto-gmail-project-zyx-8fc84fdb65ae.json"' >> ~/.zshrc
                # export GOOGLE_APPLICATION_CREDENTIALS="/Users/2024/python/code/py/auto_mail/auto-gmail-project-zyx-8fc84fdb65ae.json" >> ~/.zshrc
                # source ~/.zshrc
                # echo $GOOGLE_APPLICATION_CREDENTIALS
                'client_secret_330973435542-m8o1tqrlbjoq4n5d5uc9l1u568t0tr5e.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service