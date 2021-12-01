from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import os


class MultiEmails():
    """ Automatically send emails to multiple receives with attachments """

    def __init__(self, receiver, subject, sender='1701213756@sz.pku.edu.cn', alias=None):
        """ Initialization """
        self.receiver = receiver
        self.subject = subject
        self.receiver_alias = alias
        self.sender = sender
        self.msg = MIMEMultipart()

    def email_header(self):
        """ Email Header info """
        self.msg["Subject"] = Header(self.subject, 'utf-8')
        self.msg["From"] = self.sender
        self.msg['To'] = Header(self.receiver_alias, 'utf-8')

    def email_contents(self, contents, contents_type='plain'):
        """ text part of the contents """
        self.msg.attach(MIMEText(contents, contents_type))

    def insert_images(self, image_path, id=None):
        """
        image: path-like object
        id: use to identify image to be inserted
        """
        with open(image_path, 'rb') as f:
            image = MIMEImage(f.read())
        image.add_header('Content-ID', '<%s>' % id)
        self.msg.attach(image)

    def attachment(self, file_path):
        """ Add attachments """
        for files in file_path:
            att = MIMEText(open(files, 'rb').read(), "base64", 'utf-8')
            att["Content-Type"] = "application/octet-stream"
            att["Content-Disposition"] = 'attachment; filename= "%s"' % os.path.basename(
                files)
            self.msg.attach(att)

    def send_email(self, password, server='imap.exmail.qq.com'):
        """ login sender@server with password """
        # ssl login
        smtp = SMTP_SSL(server)
        smtp.set_debuglevel(1)  # 0 -> turn off debug
        smtp.ehlo(server)
        smtp.login(self.sender, password)
        smtp.sendmail(self.sender, self.receiver, self.msg.as_string())
        smtp.quit()
