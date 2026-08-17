from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EmailConfiguration
from .services.email_configuration_cache import EmailConfigurationCache


@receiver(post_save, sender=EmailConfiguration)
def invalidate_email_configuration_cache(sender, instance, **kwargs):
    EmailConfigurationCache.delete(instance.id)


@receiver(post_delete, sender=EmailConfiguration)
def delete_email_configuration_cache(sender, instance, **kwargs):
    EmailConfigurationCache.delete(instance.id)