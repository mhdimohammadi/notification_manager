from cryptography.fernet import Fernet
from django.conf import settings


class EncryptionService:
    PREFIX = "ENC:"


    def __init__(self):
        self.fernet = Fernet(settings.EMAIL_ENCRYPTION_KEY.encode())



    def encrypt(self, value: str) -> str:
        if value.startswith(self.PREFIX):
            return value
        encrypted = self.fernet.encrypt(value.encode()).decode()
        return f"{self.PREFIX}{encrypted}"


    def decrypt(self, value: str) -> str:
        if not value.startswith(self.PREFIX):
            raise ValueError("Value is not encrypted.")

        encrypted = value.removeprefix(self.PREFIX)
        return self.fernet.decrypt(encrypted.encode()).decode()