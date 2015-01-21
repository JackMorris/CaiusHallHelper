import smtplib
import unicodedata

_USERNAME = None
_PASSWORD = None


def set_email_credentials(username, password):
    """ Set the credentials to use for sending emails.
    :param username: gmail username for sending emails
    :param password: gmail password for sending emails
    """
    global _USERNAME, _PASSWORD
    _USERNAME = username
    _PASSWORD = password


def send_email(user, body):
    """ Send email to user.
    :param user: User instance to send the email to
    :param body: body for the email (HTML)
    """
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

    # Ensure our body is ascii
    body = unicodedata.normalize('NFKD', body).encode('ascii', 'ignore')

    recipient = user.crsid + "@cam.ac.uk"
    headers = ['From: CaiusHallHelper <' + _USERNAME + '>',
                'Subject: CaiusHallHelper',
                'To: " + recipient',
                'MIME-Version: 1.0',
                'Content-Type: text/html']
    headers = '\r\n'.join(headers)

    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.login(_USERNAME, _PASSWORD)
    session.sendmail(_USERNAME, recipient, headers + '\r\n\r\n' + body)
    session.quit()