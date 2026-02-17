import random
import string

def generate_user_id(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_user_name(user_id: str) -> str:
    return f"User_{user_id[:4]}"
