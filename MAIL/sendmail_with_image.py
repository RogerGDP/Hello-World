# -*- coding: utf-8 -*-

import smtplib
from email.header import Header
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr


# Format the email address.
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendMail(IMAGENAME):
    # Third party SMTP service.
    mail_host = "smtp.163.com"  # Set up the server
    mail_host_port = 465

    mail_user = "correct_prd_mail"  # The user name
    mail_pass = "123abc123abc"  # Authorization code

    sender = "correct_prd_mail@163.com"
    receivers = ['a434718806@126.com']  # Receive mail

    # 邮件对象:
    message = MIMEMultipart()
    message['From'] = _format_addr('树莓派检测模块 <%s>' % sender)
    message['To'] = _format_addr('管理员 <%s>' % receivers[0])
    message['Subject'] = Header('来自 raspberry 的问候 ……', 'utf-8').encode()

    # 邮件正文是MIMEText:
    message.attach(MIMEText('thera is someone here, now send message with the image...', 'plain', 'utf-8'))

    # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
    with open('../IMAGE/' + IMAGENAME, 'rb') as f:
        # 设置附件的MIME和文件名，这里是jpg类型:
        mime = MIMEBase('image', 'jpg', filename=IMAGENAME)
        # 加上必要的头信息:
        mime.add_header('Content-Disposition', 'attachment', filename=IMAGENAME)
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        # 把附件的内容读进来:
        mime.set_payload(f.read())
        # 用Base64编码:
        encoders.encode_base64(mime)
        # 添加到MIMEMultipart:
        message.attach(mime)

    try:
        smtpObj = smtplib.SMTP(mail_host)
        # smtpObj.set_debuglevel(1)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"