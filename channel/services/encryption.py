from cryptography.fernet import Fernet
from django.conf import settings


class EncryptionService:
    def __init__(self):
        self.fernet = Fernet(settings.EMAIL_ENCRYPTION_KEY.encode())



    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()


    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()