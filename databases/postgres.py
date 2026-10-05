from databases.base import DatabaseAdapter
from config.settings import PostgresConfig 
import subprocess
from error_handling import BackupTypeNotSupportedError

class Postgres(DatabaseAdapter):
    def __init__(self, config: PostgresConfig):
        super().__init__(config)
        self._env = {
            **os.environ,
            "PGHOST": config.host,
            "PGPORT": str(config.port),
            "PGUSER": config.user,
            "PGPASSWORD": config.password,
            "PGDATABASE": config.database,
        }

    # ---------------------------------------------------------
    # Core Command Runner (Keeps the file clean and DRY)
    # ---------------------------------------------------------
    def _run_cmd(self, command: list, timeout: int = 60, success_msg: str = "") -> subprocess.CompletedProcess | None:
        try:
            result = subprocess.run(command, env=self._env, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0 and success_msg:
                print(success_msg)
            elif result.returncode != 0:
                print(f"Command failed: {result.stderr.strip()}")
            return result
        except FileNotFoundError:
            print(f"Error: '{command[0]}' is not installed or not in your system PATH.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


    # ---------------------------------------------------------
    # Database Operations
    # ---------------------------------------------------------
    def test_connection(self):
        res = self._run_cmd(['pg_isready'], timeout=10, success_msg="Connection successful!")
        return res is not None and res.returncode == 0

    def _create_logical_slot(self, slot_name: str):
        # Tells Postgres to start tracking changes for a specific slot.
        query = f"SELECT pg_create_logical_replication_slot('{slot_name}', 'wal2json');"
        res = self._run_cmd(["psql", "-t", "-A", "-c", query], timeout=10)
        
        if res and res.returncode != 0 and "already exists" not in res.stderr:
            print(f"Warning: Could not create slot {slot_name}. Error: {res.stderr.strip()}")

    def dump_full_data(self, output_path: str):
        tmp = output_path + ".partial"
        res = self._run_cmd(['pg_dump', '-Fc', '-f', tmp], timeout=60)
        if res and res.returncode == 0:
            os.replace(tmp, output_path)
            print("Full dump successful!")
            self._create_logical_slot("blurz_inc_slot")
            self._create_logical_slot("blurz_diff_slot")
            return True
            
        # Clean up the corrupted partial file if it failed
        try:
            os.remove(tmp)
        except FileNotFoundError:
            pass
        return False
        
    def _read_logical_slot(self, slot_name: str, function: str, output_path: str):
        # Reads changes from a logical slot and saves the raw JSON to a file.
        query = f"SELECT data FROM {function}('{slot_name}', NULL, NULL);"
        res = self._run_cmd(["psql", "-t", "-A", "-c", query], timeout=300)
        
        if res and res.returncode == 0:
            with open(output_path, 'w') as f:
                f.write(res.stdout)
            print(f"Logical backup saved to {output_path}!")
            return True
        return False

    def dump_incremental_data(self, output_path: str):
        # Incremental backup using Logical Decoding (consumes the slot).
        print("Starting logical incremental backup...")
        return self._read_logical_slot("blurz_inc_slot", "pg_logical_slot_get_changes", output_path)

    def dump_differential_data(self, output_path: str):
        # Differential backup using Logical Decoding (peeks the slot without consuming).
        print("Starting logical differential backup...")
        return self._read_logical_slot("blurz_diff_slot", "pg_logical_slot_peek_changes", output_path)

    def restore_backup(self, backup_file_path: str):
        # Restore a custom format backup file using pg_restore.
        res = self._run_cmd(
            ['pg_restore', '--clean', '--if-exists', '-d', self._env["PGDATABASE"], backup_file_path], 
            timeout=120, 
            success_msg="Restore completed successfully!"
        )
        return res is not None and res.returncode == 0

    def get_db_info(self) -> dict:
        # Retrieve basic metadata about the PostgreSQL database.
        query = (
            "SELECT version(), pg_database_size(current_database()), "
            "(SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public');"
        )
        res = self._run_cmd(["psql", "-t", "-A", "-F", "|", "-c", query], timeout=10)
        
        if not res or res.returncode != 0:
            return {"error": res.stderr.strip() if res else "Command failed"}

        parts = res.stdout.strip().split("|")
        return {
            "db_type": "postgres",
            "host": self._env.get("PGHOST"),
            "database": self._env.get("PGDATABASE"),
            "version": parts[0] if len(parts) > 0 else "unknown",
            "size_bytes": int(parts[1]) if len(parts) > 1 else 0,
            "tables_count": int(parts[2]) if len(parts) > 2 else 0,
        }
