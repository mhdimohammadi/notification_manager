from email.utils import formataddr
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from ..models import EmailConfiguration
import smtplib
import socket
from .exceptions import EmailTimeoutError,EmailConnectionError,EmailAuthenticationError,EmailConfigurationError
from .encryption import EncryptionService
from cryptography.fernet import InvalidToken

class EmailSender:
    def __init__(self, configuration: EmailConfiguration):
        self.configuration = configuration

    def send(self, *, to, subject, body, html_body=None, cc=None, bcc=None, ):
        config = self.configuration
        encryption_service = EncryptionService()
        try :
            password = encryption_service.decrypt(config.password)
        except (InvalidToken,ValueError) as exc:
            raise EmailConfigurationError("Email configuration contains an invalid encrypted password.") from exc

        connection = EmailBackend(
            host=config.host,
            port=config.port,
            username=config.username,
            password=password,
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

        except (smtplib.SMTPConnectError,socket.gaierror) as exc:
            raise EmailConnectionError("SMTP connection failed.") from exc

        except (TimeoutError,socket.timeout) as exc:
            raise EmailTimeoutError("Email connection timed out.") from exc



