from dataclasses import dataclass


@dataclass(frozen=True)
class EmailConfigurationData:
    id: int
    host: str
    port: int
    username: str
    password: str
    from_email: str
    display_name: str
    use_tls: bool
    use_ssl: bool
    timeout: int