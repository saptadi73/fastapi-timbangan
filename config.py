from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Konfigurasi aplikasi FastAPI dari file .env"""
    
    # API Settings
    app_name: str = "FastAPI Timbangan"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Settings
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # Database Settings
    database_url: str = "postgresql://opnpg:openpgpwd@localhost:5432/timbangan"
    sqlalchemy_echo: bool = False
    
    # Security Settings
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Scale/Timbangan Settings
    scale_port: str = "COM3"
    scale_baudrate: int = 2400
    scale_bytesize: int = 8
    scale_stopbits: int = 1
    scale_parity: str = "N"
    scale_reconnect_ms: int = 3000
    scale_poll_ms: int = 1000
    scale_enable_poll: bool = True
    scale_auto_start: bool = True
    
    # Other Settings
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Inisialisasi settings
settings = Settings()

