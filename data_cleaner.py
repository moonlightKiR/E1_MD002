from typing import List, Dict, Any
from models import User  # Importamos el modelo User del nuevo archivo models.py


def remove_duplicates(users: List[Dict[str, Any]], unique_key: str = 'email') -> List[Dict[str, Any]]:
    """
    Removes duplicate users based on a unique key (default is 'email').
    Supports nested keys like 'login.uuid'.
    """
    seen = set()
    unique_users = []

    for user in users:
        # Access nested keys (e.g., "login.uuid")
        value = user
        for part in unique_key.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break

        if value not in seen:
            seen.add(value)
            unique_users.append(user)

    return unique_users


def clean_and_deduplicate_users(users: List[User]) -> List[Dict[str, Any]]:
    """
    Performs two main cleaning steps:
    1. Removes users with critical missing (None) values.
    2. Removes duplicates based on email.

    Returns: A list of unique, cleaned user data (as dictionaries).
    """
    # 1. Remove Nuls (Critical fields only)
    cleaned_users_objects = [
        user for user in users
        if (
                user.email
                and user.login.password is not None
                and user.location.country
                and user.dob.age is not None
        )
    ]

    # Convert Pydantic objects to dictionaries for the deduplication step
    users_data_dict = [user.model_dump() for user in cleaned_users_objects]

    # 2. Remove Duplicates
    final_unique_users_data = remove_duplicates(users_data_dict, unique_key='email')

    # Log information (optional, moved to main.py for better separation)
    return final_unique_users_data