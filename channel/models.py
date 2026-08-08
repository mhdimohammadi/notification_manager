from django.db import models
from django.core.exceptions import ValidationError


class Channel(models.Model):
    class ChannelType(models.TextChoices):
        EMAIL = 'email', 'email'
        TELEGRAM = 'telegram', 'telegram'
        SMS = 'sms', 'sms'

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=ChannelType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "channel"
        verbose_name_plural = "channels"

    def __str__(self):
        return self.name


class EmailConfiguration(models.Model):
    channel = models.OneToOneField(Channel, on_delete=models.CASCADE, related_name="email_configuration", null=True,
                                   blank=True)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    from_email = models.EmailField()
    display_name = models.CharField(max_length=100)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    timeout = models.PositiveIntegerField(default=30)

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"

    def clean(self):
        super().clean()

        if not self.channel_id:
            return

        if self.channel.type != Channel.ChannelType.EMAIL:
            raise ValidationError({
                "channel": "Selected channel must be of type Email."})

        if self.use_tls and self.use_ssl:
            raise ValidationError({
                "use_tls": "TLS and SSL cannot both be enabled.",
                "use_ssl": "TLS and SSL cannot both be enabled."
            })

        if not self.use_tls and not self.use_ssl:
            raise ValidationError({
                "use_tls": "Either TLS or SSL must be enabled.",
                "use_ssl": "Either TLS or SSL must be enabled."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.channel.name
