import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

# ---------------------------------------------------------
#  .env loader
# ---------------------------------------------------------
def load_env_file(filepath: str = ".env"):
    """Natively parse a .env file and load it into os.environ."""
    if not os.path.exists(filepath):
        return
        
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            # Ignore empty lines and comments
            if not line or line.startswith("#"):
                continue
                
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


# ---------------------------------------------------------
# Database Configurations (Native Python Dataclasses)
# ---------------------------------------------------------
@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @classmethod
    def from_env(cls, prefix: str):
        """Helper to natively load this config from environment variables."""
        # We use int() for port, with a fallback of 0 if it's missing.
        port_str = os.getenv(f"{prefix}_PORT", "0")
        
        return cls(
            host=os.getenv(f"{prefix}_HOST", ""),
            port=int(port_str) if port_str.isdigit() else 0,
            user=os.getenv(f"{prefix}_USER", ""),
            password=os.getenv(f"{prefix}_PASSWORD", ""),
            database=os.getenv(f"{prefix}_DATABASE", "")
        )



class PostgresConfig(DatabaseConfig):
    pass

class MysqlConfig(DatabaseConfig):
    pass

class MongoConfig(DatabaseConfig):
    pass

class SqlServerConfig(DatabaseConfig):
    pass


# ---------------------------------------------------------
# Cloud & Storage Provider Configurations
# ---------------------------------------------------------
@dataclass
class AzureBlobStorageConfig:
    connection_string: str
    container_name: str

    @classmethod
    def from_env(cls):
        return cls(
            connection_string=os.getenv("AZURE_CONNECTION_STRING", ""),
            container_name=os.getenv("AZURE_CONTAINER_NAME", "")
        )


@dataclass
class GoogleCloudStorageConfig:
    bucket_name: str
    credentials: str 

    @classmethod
    def from_env(cls):
        return cls(
            bucket_name=os.getenv("GCP_BUCKET_NAME", ""),
            credentials=os.getenv("GCP_CREDENTIALS", "")
        )


@dataclass
class S3Config:
    access_key_id: str
    secret_access_key: str
    bucket_name: str

    @classmethod
    def from_env(cls):
        return cls(
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            bucket_name=os.getenv("AWS_BUCKET_NAME", "")
        )


@dataclass
class LocalStorageConfig:
    path: Path

    @classmethod
    def from_env(cls):
        path_str = os.getenv("LOCAL_PATH", "./backup-data")
        return cls(path=Path(path_str))