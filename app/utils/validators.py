"""Input validation utilities"""

import re
from typing import Optional, Tuple
from datetime import datetime


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, None
    return False, "Invalid email format"


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's a valid phone number (10-15 digits, optional + prefix)
    pattern = r'^\+?[1-9]\d{9,14}$'
    if re.match(pattern, cleaned):
        return True, None
    return False, "Invalid phone number format"


def validate_amount(amount_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validate and parse amount string
    
    Returns:
        Tuple of (is_valid, parsed_amount, error_message)
    """
    try:
        amount = float(amount_str)
        if amount <= 0:
            return False, None, "Amount must be greater than 0"
        if amount > 10000000:  # 10 million max
            return False, None, "Amount is too large"
        return True, amount, None
    except ValueError:
        return False, None, "Invalid amount format. Use numbers only (e.g., 1000.50)"


def validate_quantity(quantity_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate and parse quantity string
    
    Returns:
        Tuple of (is_valid, parsed_quantity, error_message)
    """
    try:
        quantity = int(quantity_str)
        if quantity < 0:
            return False, None, "Quantity cannot be negative"
        if quantity > 1000000:
            return False, None, "Quantity is too large"
        return True, quantity, None
    except ValueError:
        return False, None, "Invalid quantity format. Use whole numbers only"


def validate_date(date_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate and parse date string (YYYY-MM-DD format)
    
    Returns:
        Tuple of (is_valid, parsed_date, error_message)
    """
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return True, dt.strftime("%Y-%m-%d"), None
        except ValueError:
            continue
    
    return False, None, "Invalid date format. Use YYYY-MM-DD (e.g., 2024-12-25)"


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if re.match(pattern, url):
        return True, None
    return False, "Invalid URL format. Must start with http:// or https://"


def validate_uuid(uuid_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate UUID format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if re.match(pattern, uuid_str.lower()):
        return True, None
    return False, "Invalid ID format"


def validate_text_length(text: str, min_length: int = 1, max_length: int = 1000) -> Tuple[bool, Optional[str]]:
    """
    Validate text length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    length = len(text)
    if length < min_length:
        return False, f"Text is too short. Minimum {min_length} characters required"
    if length > max_length:
        return False, f"Text is too long. Maximum {max_length} characters allowed"
    return True, None


def parse_command_args(text: str, expected_args: int) -> Tuple[bool, list, Optional[str]]:
    """
    Parse command arguments from text
    
    Args:
        text: Full command text
        expected_args: Number of expected arguments
    
    Returns:
        Tuple of (is_valid, args_list, error_message)
    """
    parts = text.split(maxsplit=expected_args)
    
    # Remove command itself
    if len(parts) > 0:
        parts = parts[1:]
    
    if len(parts) < expected_args:
        return False, [], f"Expected {expected_args} arguments, got {len(parts)}"
    
    return True, parts, None
