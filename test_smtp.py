
from aiosmtplib import SMTP, SMTPException
from traceback import print_exc
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

msg = MIMEText("TEST SMTP", "html", "utf-8")

async def test_smtp():
    user_name = 'LenovoATS_Compal@Compal.com;'
    msg['From'] = user_name

    # msg['Cc'] = 'wenys1@lenovo.com'
    msg['Subject'] = 'TEST SMTP - Compal'
    try:
        print('Ready to send E-Mail')
        async with SMTP(hostname='10.128.2.181', port=25, use_tls=False, validate_certs=True) as smtp:
            print('Start send E-Mail')
            await smtp.send_message(msg)
            print('Send E-Mail Success')
            await smtp.quit()
            smtp.close()
            print('SMTP connect close')
            return True
    except BaseException as e:
        print("Failed to send email: ")
        print_exc()
        return False


asyncio.run(test_smtp())
