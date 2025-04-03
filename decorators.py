import logging
import functools
from mcp import McpError

logger = logging.getLogger(__name__)
_privilege_granted = False  # Module-level state variable


class PrivilegeError(Exception):
    """Custom exception for privilege errors."""

    pass


def require_privilege(func):
    """
    Decorator to ensure temporary privilege has been granted via module state
    before executing a sensitive function. Resets privilege after execution.
    Raises an McpError if privilege is not granted.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _privilege_granted
        if _privilege_granted:
            _privilege_granted = False
            return func(*args, **kwargs)
        else:
            logger.warning(
                f"Attempted sensitive operation '{func.__name__}' without privilege."
            )
            raise McpError(
                PrivilegeError(
                    f"Operation '{func.__name__}' requires privilege. Use 'grant_privilege' first."
                )
            )

    return wrapper


def handle_errors_as_mcp(func):
    """
    Decorator to catch any exception from the wrapped function, log it,
    and re-raise it wrapped in McpError.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error during operation '{func.__name__}': {e}")
            if isinstance(e, McpError):
                raise e
            else:
                raise McpError(e)

    return wrapper


def grant_privilege() -> bool:
    """
    Grants temporary privilege for the next sensitive operation.
    Returns True.
    """
    global _privilege_granted
    _privilege_granted = True
    logger.info("Temporary privilege granted for next sensitive operation.")
    return True
