from datetime import datetime
import os

def current_datetime():
    """
    Get the current datetime in ISO format.
    
    Returns:
        str: Current datetime in ISO format
    """
    # You can also use environment variables to customize the format
    format_str = os.environ.get('DATETIME_FORMAT', '%Y-%m-%dT%H:%M:%SZ')
    return datetime.now().strftime(format_str)