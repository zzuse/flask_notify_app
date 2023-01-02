from server.utils.smtp_client import EmailClient


def send_mail():
    html = """\
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           How are you?<br>
           Here is the <a href="http://www.python.org">link</a> you wanted.
        </p>
      </body>
    </html>
    """
    ec = EmailClient()
    ec.set_subject("Test Email Sending")
    #ec.set_plain_text("This is the body of the message.")
    ec.set_html_text(html)
    ec.set_to_address("l@xxx.com")
    #ec.set_to_addresses(["c@xxx.com", "f@xxx.com", "y@xxx.com", "z@xxx.com"])
    ec.send()

