# role_enum.py
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"
