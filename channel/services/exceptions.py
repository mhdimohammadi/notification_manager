class EmailSenderError(Exception):
    """Base exception for email sender errors."""


class EmailConnectionError(EmailSenderError):
    """Raised when connection to SMTP server fails."""


class EmailAuthenticationError(EmailSenderError):
    """Raised when SMTP authentication fails."""


class EmailTimeoutError(EmailSenderError):
    """Raised when SMTP operation times out."""



class EmailConfigurationError(EmailSenderError):
    """Raised when email configuration or encrypted credentials are invalid."""