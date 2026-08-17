from django.core.cache import cache


class NotificationIdempotency:
    PREFIX = "notification:idempotency:"
    TTL = 60 * 60 * 24
    PROCESSING = "processing"

    @classmethod
    def _key(cls, idempotency_key):
        return f"{cls.PREFIX}{idempotency_key}"

    @classmethod
    def claim(cls, idempotency_key):
        return cache.add(cls._key(idempotency_key),cls.PROCESSING,timeout=cls.TTL)

    @classmethod
    def set_result(cls, idempotency_key, notification_id):
        cache.set(cls._key(idempotency_key),notification_id,timeout=cls.TTL)

    @classmethod
    def get(cls, idempotency_key):
        return cache.get(cls._key(idempotency_key))

    @classmethod
    def delete(cls, idempotency_key):
        return cache.delete(cls._key(idempotency_key))
