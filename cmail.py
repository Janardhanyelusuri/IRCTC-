import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('janardhanyelusuri58233@gmail.com','uocm chsj kixs oeag')
    msg=EmailMessage()
    msg['From']='jahanshaik9990@gmail.com'
    msg['Subject']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()
