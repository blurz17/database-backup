# ==============================================================================
# 1. BASE EXCEPTION
# ==============================================================================
class BackupUtilityError(Exception):
    """Grandparent exception. Catch this at the CLI entry point to prevent hard crashes."""
    pass


# ==============================================================================
# 2. DATABASE DOMAIN (Connectivity & Syntax Errors)
# ==============================================================================
class DatabaseError(BackupUtilityError):
    """Base for all database issues."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised for timeouts, unreachable hosts, or bad network strings."""
    pass

class DatabaseCredentialError(DatabaseError):
    """Raised specifically when username/password/auth-token fails validation."""
    pass

class UnsupportedDatabaseTypeError(DatabaseError):
    """Raised if a user requests a DBMS your tool doesn't support yet (e.g., Oracle)."""
    pass


# ==============================================================================
# 3. BACKUP & RESTORE UTILITY DOMAIN (Process Errors)
# ==============================================================================
class OperationError(BackupUtilityError):
    """Base for backup, restore, or compression execution failures."""
    pass

class BackupExecutionError(OperationError):
    """Raised if pg_dump, mysqldump, or mongodump binaries fail mid-process."""
    pass

class RestoreExecutionError(OperationError):
    """Raised if the restore binary fails or input backup file is corrupted."""
    pass

class BackupTypeNotSupportedError(OperationError):
    """Raised if user asks for 'incremental' on a DB engine that only supports 'full'."""
    pass

class CompressionError(OperationError):
    """Raised if disk runs out of space during zipping or tarring."""
    pass


# ==============================================================================
# 4. STORAGE & CLOUD DOMAIN (Target Destination Errors)
# ==============================================================================
class StorageError(BackupUtilityError):
    """Base for all target destination issues."""
    pass

class LocalStorageError(StorageError):
    """Raised if directory lacks write permissions or local path doesn't exist."""
    pass

class CloudStorageError(StorageError):
    """Raised for AWS/GCS/Azure API errors, missing bucket permissions, or network drops."""
    pass


# ==============================================================================
# 5. INTEGRATIONS & NOTIFICATIONS DOMAIN (Side-Effect Errors)
# ==============================================================================
class IntegrationError(BackupUtilityError):
    """Raised if Slack webhooks timeout or fail, without stopping the core backup."""
    pass

