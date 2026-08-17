from django.core.cache import cache
from .email_configuration_data import EmailConfigurationData


class EmailConfigurationCache:
    PREFIX = "notification_manager:email_configuration"
    TIMEOUT = 3600

    @classmethod
    def _key(cls, configuration_id):
        return f"{cls.PREFIX}:{configuration_id}"

    @classmethod
    def _to_data(cls, configuration):
        return EmailConfigurationData(
            id=configuration.id,
            host=configuration.host,
            port=configuration.port,
            username=configuration.username,
            password=configuration.password,
            from_email=configuration.from_email,
            display_name=configuration.display_name,
            use_tls=configuration.use_tls,
            use_ssl=configuration.use_ssl,
            timeout=configuration.timeout)

    @classmethod
    def get(cls, configuration_id):
        return cache.get(cls._key(configuration_id))

    @classmethod
    def set(cls, configuration):
        data = cls._to_data(configuration)
        cache.set(cls._key(configuration.id), data, timeout=cls.TIMEOUT)
        return data

    @classmethod
    def delete(cls, configuration_id):
        cache.delete(cls._key(configuration_id))
