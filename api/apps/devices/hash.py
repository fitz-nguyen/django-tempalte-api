import hashlib


def hash_device_id(device_id: str) -> str:
    return hashlib.sha256(device_id.encode()).hexdigest()
