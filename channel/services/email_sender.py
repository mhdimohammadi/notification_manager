from email.utils import formataddr
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from ..models import EmailConfiguration
import socket
import smtplib
from .exceptions import EmailTimeoutError,EmailConnectionError,EmailAuthenticationError


class EmailSender:
    def __init__(self, configuration: EmailConfiguration):
        self.configuration = configuration

    def send(self, *, to, subject, body, html_body=None, cc=None, bcc=None, ):
        config = self.configuration

        connection = EmailBackend(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            use_tls=config.use_tls,
            use_ssl=config.use_ssl,
            timeout=config.timeout)

        from_email = formataddr((config.display_name, config.from_email))

        message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=from_email, to=to, cc=cc, bcc=bcc, connection=connection, )

        if html_body:
            message.attach_alternative(html_body, "text/html", )
        try :
            return message.send()
        except smtplib.SMTPAuthenticationError as exc:
            raise EmailAuthenticationError("SMTP authentication failed.") from exc

        except smtplib.SMTPConnectError as exc:
            raise EmailConnectionError("SMTP connection failed.") from exc

        except (TimeoutError,socket.timeout) as exc:
            raise EmailTimeoutError("Email connection timed out.") from exc
