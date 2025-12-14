"""Message parsing utilities for extracting structured data from Telegram messages"""

from typing import Dict, Optional, Any, List
from pydantic import ValidationError
from decimal import Decimal, InvalidOperation
from datetime import datetime


class MessageParser:
    """Parse structured data from Telegram messages"""
    
    @staticmethod
    def parse_key_value_message(message_text: str) -> Dict[str, str]:
        """
        Parse a message with key-value pairs.
        
        Example:
            Amount: 1500
            Description: Office supplies
            Date: 2025-12-14
            
        Returns:
            Dict with lowercase keys and stripped values
        """
        lines = message_text.strip().split('\n')
        data = {}
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                data[key] = value
        
        return data
    
    @staticmethod
    def normalize_field_name(field: str, aliases: Dict[str, List[str]]) -> Optional[str]:
        """
        Normalize field name using aliases.
        
        Args:
            field: The field name to normalize
            aliases: Dict mapping canonical names to list of aliases
            
        Returns:
            Canonical field name or None if not found
        """
        field_lower = field.lower()
        
        for canonical, alias_list in aliases.items():
            if field_lower in [a.lower() for a in alias_list]:
                return canonical
        
        return None
    
    @staticmethod
    def parse_amount(value: str) -> Optional[Decimal]:
        """
        Parse amount from string, handling various formats.
        
        Examples:
            "1500" -> 1500
            "1,500" -> 1500
            "1500.50" -> 1500.50
            "₹1500" -> 1500
        """
        try:
            # Remove currency symbols and commas
            cleaned = value.replace('₹', '').replace('$', '').replace(',', '').strip()
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    @staticmethod
    def parse_date(value: str) -> Optional[datetime]:
        """
        Parse date from string, supporting multiple formats.
        
        Formats supported:
            - YYYY-MM-DD
            - DD/MM/YYYY
            - DD-MM-YYYY
        """
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def extract_field_with_aliases(
        data: Dict[str, str],
        canonical_name: str,
        aliases: List[str]
    ) -> Optional[str]:
        """
        Extract field value using canonical name and aliases.
        
        Args:
            data: Parsed key-value data
            canonical_name: The canonical field name
            aliases: List of possible aliases for the field
            
        Returns:
            Field value or None
        """
        all_names = [canonical_name] + aliases
        
        for name in all_names:
            name_lower = name.lower()
            if name_lower in data:
                return data[name_lower]
        
        return None


class ExpenseMessageParser(MessageParser):
    """Parser specifically for expense messages"""
    
    FIELD_ALIASES = {
        'amount': ['amount', 'amt', 'price', 'cost', 'total'],
        'description': ['description', 'desc', 'detail', 'details', 'title'],
        'date': ['date', 'transaction date', 'expense date', 'when'],
        'category': ['category', 'cat', 'type', 'tag'],
    }
    
    @classmethod
    def parse(cls, message_text: str) -> Dict[str, Any]:
        """
        Parse expense data from message text.
        
        Returns:
            Dict with normalized field names and parsed values
        """
        raw_data = cls.parse_key_value_message(message_text)
        parsed = {}
        
        # Parse amount
        amount_str = cls.extract_field_with_aliases(
            raw_data, 'amount', cls.FIELD_ALIASES['amount']
        )
        if amount_str:
            parsed['amount'] = cls.parse_amount(amount_str)
        
        # Parse description
        description = cls.extract_field_with_aliases(
            raw_data, 'description', cls.FIELD_ALIASES['description']
        )
        if description:
            parsed['description'] = description
        
        # Parse date
        date_str = cls.extract_field_with_aliases(
            raw_data, 'date', cls.FIELD_ALIASES['date']
        )
        if date_str:
            date_obj = cls.parse_date(date_str)
            if date_obj:
                parsed['transaction_date'] = date_obj.date()
        
        # Parse category
        category = cls.extract_field_with_aliases(
            raw_data, 'category', cls.FIELD_ALIASES['category']
        )
        if category:
            parsed['category'] = category
        
        return parsed
    
    @classmethod
    def validate_required_fields(cls, parsed_data: Dict[str, Any]) -> List[str]:
        """
        Validate that required fields are present and valid.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if 'amount' not in parsed_data or parsed_data['amount'] is None:
            errors.append("❌ Amount is required and must be a valid number")
        elif parsed_data['amount'] <= 0:
            errors.append("❌ Amount must be greater than zero")
        
        if 'description' not in parsed_data or not parsed_data['description']:
            errors.append("❌ Description is required")
        
        return errors


def parse_command_args(command_text: str, expected_args: int = 0) -> tuple[bool, List[str], Optional[str]]:
    """
    Parse command arguments from text.
    
    Args:
        command_text: Full command text (e.g., "/expense abc123")
        expected_args: Number of expected arguments
        
    Returns:
        Tuple of (is_valid, args_list, error_message)
    """
    parts = command_text.strip().split()
    
    if len(parts) < 1:
        return False, [], "Invalid command format"
    
    # Remove the command itself
    args = parts[1:]
    
    if expected_args > 0 and len(args) < expected_args:
        return False, args, f"Expected {expected_args} argument(s), got {len(args)}"
    
    return True, args, None
