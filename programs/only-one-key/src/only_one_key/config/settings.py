 # config settings ->

from pathlib import Path

__all__ = ["APP_NAME", "DATA_DIR", "LOCK_FILE", "SALT_FILE", "VAULT_FILE", "PBKDF2_ITERATIONS", "SALT_LENGTH"]

APP_NAME = "Only One Key"

 # user data directory ->
DATA_DIR = Path.home() / ".only_one_key"

 # files inside data directory ->
LOCK_FILE = DATA_DIR / "lock.argon2"
SALT_FILE = DATA_DIR / "salt.bin"
VAULT_FILE = DATA_DIR / "vault.rzt"

 # crypto params ->
SALT_LENGTH = 16
PBKDF2_ITERATIONS = 480_000
