import configparser
import os
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
    
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


score_url = 'https://pkuhelper.pku.edu.cn/api_xmcp/isop/scores?user_token='
sleeping_time = float(config.get('client', 'refresh_interval'))
user_token = str(config.get('user', 'user_token'))
from_email= str(config.get('sender', 'sender'))
from_host= str(config.get('sender', 'sender_host'))
from_port= int(config.get('sender', 'sender_port'))
from_token= str(config.get('sender', 'sender_token'))
receivers = [str(config.get('receiver', 'receiver'))]
email_subject = str(config.get('email', 'email_subject'))
email_message = str(config.get('email', 'email_message'))


def get_score(user_token):
    r = requests.get(score_url+user_token)
    score = r.json()
    if score['success']:
        return True,score
    else:
        print("Error when trying to get grades.")
        print(score)
        print()
        return False,score

def send_email(msg):
    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = from_email
    message['To'] = receivers[0]
    subject = email_subject
    message['Subject'] = Header(subject, 'utf-8')
    smtpObj = smtplib.SMTP_SSL(from_host, from_port)
    smtpObj.login(from_email, from_token)
    smtpObj.sendmail(from_email, receivers, message.as_string())
    return True

ok = True
if os.path.exists("score") == False:
    ok, score = get_score(user_token)
    if ok:
        with open("score", "w") as f:
            f.write(str(score))

while ok:
    ok, score = get_score(user_token)
    if ok:
        with open("score", "r") as f:
            old_score = f.readline()
        if old_score == str(score):
            print("No Grades Updated. Checked at "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            time.sleep(sleeping_time)
        else:
            print("New Grades Updated!")
            send_email(email_message)
            with open("score", "w") as f:
                f.write(str(score))
        
