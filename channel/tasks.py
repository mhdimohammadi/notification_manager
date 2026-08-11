from celery import shared_task
from .models import EmailConfiguration
from .services.email_sender import EmailSender
from .services.exceptions import EmailConnectionError,EmailAuthenticationError,EmailTimeoutError

@shared_task(bind=True,max_retries=3)
def send_email(self,configuration_id, *, to, subject, body, html_body=None, cc=None, bcc=None, ):
    configuration = EmailConfiguration.objects.get(pk=configuration_id)
    sender = EmailSender(configuration)
    try :
        return sender.send(to=to,subject=subject,body=body,html_body=html_body,cc=cc,bcc=bcc,)

    except EmailAuthenticationError :
        raise

    except (EmailTimeoutError,EmailConnectionError) as exc :
        countdown = 10 * (2 ** self.request.retries)
        raise self.retry(exc=exc,countdown=countdown)

