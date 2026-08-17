from enum import Enum
from typing import List, Dict, Any
from src.backend.config import settings
from loguru import logger


class Permission(str, Enum):
    FS_READ = "FS_READ"
    FS_WRITE = "FS_WRITE"
    FS_DELETE = "FS_DELETE"
    EMAIL_SEND = "EMAIL_SEND"
    WHATSAPP_SEND = "WHATSAPP_SEND"
    SYS_EXEC = "SYS_EXEC"
    BROWSER_AUTO = "BROWSER_AUTO"


class PermissionManager:
    """Granular Permission System for sandboxed tool execution."""
    def __init__(self):
        self._granted_permissions: Dict[Permission, bool] = {
            Permission.FS_READ: True,
            Permission.FS_WRITE: settings.ALLOW_FS_WRITE,
            Permission.FS_DELETE: settings.ALLOW_FS_DELETE,
            Permission.EMAIL_SEND: True,
            Permission.WHATSAPP_SEND: settings.ALLOW_WHATSAPP_AUTO,
            Permission.SYS_EXEC: settings.ALLOW_SYS_EXEC,
            Permission.BROWSER_AUTO: True,
        }

    def check_permission(self, permission: Permission) -> bool:
        """Check if a specific permission is granted."""
        granted = self._granted_permissions.get(permission, False)
        if not granted:
            logger.warning(f"PermissionManager: Permission DENIED for '{permission.value}'")
        return granted

    def grant_permission(self, permission: Permission):
        """Grant a permission at runtime."""
        self._granted_permissions[permission] = True
        logger.info(f"PermissionManager: Permission GRANTED for '{permission.value}'")

    def revoke_permission(self, permission: Permission):
        """Revoke a permission at runtime."""
        self._granted_permissions[permission] = False
        logger.info(f"PermissionManager: Permission REVOKED for '{permission.value}'")


# Global Singleton Permission Manager Instance
permission_manager = PermissionManager()
