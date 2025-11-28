"""
Logging utilities for the album app.
"""
import logging
import traceback

# Get logger instances
logger = logging.getLogger(__name__)
security_logger = logging.getLogger('django.security')
audit_logger = logging.getLogger('django.audit')


def log_security_event(event_type, user, details=None, request=None):
    """
    Log security-related events.
    
    Args:
        event_type (str): Type of security event
        user (User): User involved in the event
        details (str): Additional details about the event
        request (HttpRequest): Request object for additional context
    """
    user_info = f"User: {user.username} (ID: {user.id})" if user else "Anonymous"
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown') if request else 'Unknown'
    
    message = f"Security Event: {event_type} - {user_info} - IP: {ip_address}"
    if details:
        message += f" - Details: {details}"
    
    security_logger.warning(message)


def log_user_action(action, user, object_type=None, object_id=None, request=None):
    """
    Log user actions for audit trail.
    
    Args:
        action (str): Action performed
        user (User): User who performed the action
        object_type (str): Type of object affected
        object_id (int): ID of object affected
        request (HttpRequest): Request object for additional context
    """
    user_info = f"User: {user.username} (ID: {user.id})" if user else "Anonymous"
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown') if request else 'Unknown'
    
    message = f"User Action: {action} - {user_info} - IP: {ip_address}"
    if object_type and object_id:
        message += f" - Object: {object_type}:{object_id}"
    
    audit_logger.info(message)


def log_info(message, user=None, request=None):
    """
    Log general information.
    
    Args:
        message (str): Message to log
        user (User): User involved
        request (HttpRequest): Request object
    """
    user_info = f"User: {user.username} (ID: {user.id})" if user else "Anonymous"
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown') if request else 'Unknown'
    
    log_message = f"Info: {message} - {user_info} - IP: {ip_address}"
    logger.info(log_message)


def log_error(error, user=None, request=None, additional_context=None):
    """
    Log application errors with context.
    
    Args:
        error (Exception): The error that occurred
        user (User): User involved in the error
        request (HttpRequest): Request object for additional context
        additional_context (dict): Additional context information
    """
    user_info = f"User: {user.username} (ID: {user.id})" if user else "Anonymous"
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown') if request else 'Unknown'
    message = f"Error: {type(error).__name__}: {str(error)} - {user_info} - IP: {ip_address}"
    if additional_context:
        message += f" - Context: {additional_context}"
    
    # Include traceback in the log message
    message += f"\nTraceback:\n{traceback.format_exc()}"
    
    logger.error(message)
    
    # Log to security logger if it's a security-related error
    if any(keyword in str(error).lower() for keyword in ['permission', 'unauthorized', 'forbidden', 'security']):
        security_logger.error(f"Security Error: {message}")


def log_performance_issue(operation, duration, user=None, request=None):
    """
    Log performance issues.
    
    Args:
        operation (str): Operation that was slow
        duration (float): Duration in seconds
        user (User): User involved
        request (HttpRequest): Request object
    """
    user_info = f"User: {user.username} (ID: {user.id})" if user else "Anonymous"
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown') if request else 'Unknown'
    
    message = f"Performance Issue: {operation} took {duration:.2f}s - {user_info} - IP: {ip_address}"
    
    if duration > 5.0:  # Log as error if very slow
        logger.error(message)
    elif duration > 2.0:  # Log as warning if moderately slow
        logger.warning(message)
    else:
        logger.info(message)


class ErrorHandler:
    """Context manager for handling errors with logging."""
    
    def __init__(self, operation_name, user=None, request=None, additional_context=None):
        self.operation_name = operation_name
        self.user = user
        self.request = request
        self.additional_context = additional_context
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is not None:
            log_error(exc_val, self.user, self.request, self.additional_context)
        else:
            # Log performance if operation took too long
            if duration > 1.0:
                log_performance_issue(self.operation_name, duration, self.user, self.request)
        
        return False  # Don't suppress the exception
