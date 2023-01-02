import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from server.utils.server_logger import g_logger as logger


class EmailClient(object):

    def __init__(self, server='smtp.xxx-inc.com', port=25,
                 from_addr='auto-noreply@xxx-inc.com',
                 account='auto-noreply@xxx-inc.com',
                 password='xxx'):

        self.server = server
        self.port = port
        self.from_address = from_addr
        self.account = account
        self.password = password
        self.to_address = []
        self.subject = 'untitled'
        self.plan_text = ''
        self.html_text = ''
        self.attached = []

    def set_to_address(self, to_addr):
        self.to_address.append(to_addr)

    def set_to_addresses(self, dest_addrs):
        to_addrs = set(dest_addrs)
        for addr in to_addrs:
            self.to_address.append(addr)

    def set_subject(self, subject):
        self.subject = subject

    def set_plain_text(self, text):
        self.plan_text = text

    def set_html_text(self, text):
        self.html_text = text

    def set_attachment(self, attached):
        self.attached = attached

    def __compose__(self):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_address
        to = ","
        msg['To'] = to.join(self.to_address)
        msg['Subject'] = self.subject
        msg.add_header("Content-Type", "text/html")

        if len(self.plan_text):
            msg.attach(MIMEText(self.plan_text, 'plain', 'utf-8'))
        if len(self.html_text):
            msg.attach(MIMEText(self.html_text, 'html', 'utf-8'))

        for fn in self.attached:
            part = MIMEBase('application', 'octet-stream')
            with open(fn, "rb") as f:
                part.set_payload((f).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename=%s" % fn)
            msg.attach(part)

        return msg

    def send(self):
        msg = self.__compose__()
        s = smtplib.SMTP(self.server, self.port)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.account, self.password)
        text = msg.as_string()

        try:
            s.sendmail(self.from_address, self.to_address, text)
        finally:
            s.quit()



