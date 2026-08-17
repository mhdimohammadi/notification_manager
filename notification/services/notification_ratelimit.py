import redis
from django.conf import settings



redis_client = redis.Redis.from_url(settings.REDIS_URL,decode_responses=True)



class NotificationRateLimit:
    MAX_REQUESTS = 10
    WINDOW_SECONDS = 60

    _script = redis_client.register_script(
        """
        local current = redis.call("GET", KEYS[1])
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])

        if current == false then
            redis.call("SET", KEYS[1], 1, "EX", window)
            return 1
        end

        if tonumber(current) >= limit then
            return 0
        end

        redis.call("INCR", KEYS[1])

        return 1
        """
    )

    @classmethod
    def check(cls, identifier):
        key = f"notification:rate-limit:{identifier}"
        result = cls._script(keys=[key],args=[cls.MAX_REQUESTS,cls.WINDOW_SECONDS])
        return bool(result)