from argon2 import PasswordHasher, Type
from argon2.exceptions import *


def validate(digest: str, password: str) -> bool:
    ph = PasswordHasher(
        memory_cost=65536,
        time_cost=4,
        parallelism=2,
        hash_len=32,
        type=Type.ID
    )

    try:
        return ph.verify(digest, password)
    except (VerifyMismatchError, VerificationError, InvalidHash) as _:
        return False


__all__ = (
    validate.__name__,
)
