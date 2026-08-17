import json
import os
import re
import difflib
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
from loguru import logger

CONTACTS_FILE = Path(__file__).parent.parent / "contacts.json"


def load_contacts() -> Dict[str, str]:
    """Load address book contacts from contacts.json."""
    if not os.path.exists(CONTACTS_FILE):
        return {}
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load contacts file: {e}")
        return {}


def save_contact(name: str, value: str) -> bool:
    """Save or update a contact in contacts.json."""
    contacts = load_contacts()
    contacts[name.strip().lower()] = value.strip()
    try:
        with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2)
        logger.info(f"Saved contact '{name}': '{value}'")
        return True
    except Exception as e:
        logger.error(f"Failed to save contact '{name}': {e}")
        return False


def extract_recipient_name(query: str) -> Optional[str]:
    """Extract recipient contact name directly from user natural language query."""
    patterns = [
        r'(?:to|for)\s+([a-zA-Z0-9\s]+?)(?:\s+message|\s+saying|\s+is|\s+that|\s+with|$)',
        r'(?:whatsapp|email|mail)\s+([a-zA-Z0-9\s]+?)(?:\s+message|\s+saying|\s+is|\s+that|\s+with|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            recipient = match.group(1).strip()
            # Clean stop words from recipient
            stop_words = {"whatsapp", "email", "mail", "message", "send", "the", "a", "an"}
            words = [w for w in recipient.split() if w.lower() not in stop_words]
            if words:
                return " ".join(words)
    return None


def get_contact_details(query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fuzzy resolve contact name and value (phone or email) from user query.
    Returns (matched_name, phone_or_email) or (extracted_name, None).
    """
    contacts = load_contacts()
    recipient_name = extract_recipient_name(query)

    if not contacts:
        return (recipient_name, None)

    q = query.lower()
    stop_words = {"send", "message", "to", "email", "mail", "whatsapp", "hello", "hi", "hey", "tell", "say", "the", "my", "is"}
    query_words = [w for w in q.split() if w not in stop_words and len(w) >= 2]

    contact_names = list(contacts.keys())

    # 1. Exact match check first
    if recipient_name and recipient_name.lower() in contacts:
        matched = recipient_name.lower()
        return (matched.capitalize(), contacts[matched])

    for word in query_words:
        if word in contacts:
            return (word.capitalize(), contacts[word])

    # 2. Fuzzy match check with cutoff=0.6
    for word in query_words:
        matches = difflib.get_close_matches(word, contact_names, n=1, cutoff=0.6)
        if matches:
            matched_name = matches[0]
            logger.info(f"Fuzzy matched contact word '{word}' -> '{matched_name}'")
            return (matched_name.capitalize(), contacts[matched_name])

    return (recipient_name.capitalize() if recipient_name else None, None)


def get_contact_value(query: str) -> Optional[str]:
    """Backward compatibility helper returning just the value."""
    name, val = get_contact_details(query)
    return val
