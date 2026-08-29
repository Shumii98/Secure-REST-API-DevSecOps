from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

# Demo users for the authentication flow.
# In a real system, this would be a database table.
USERS = {
    "security-user": {
        "username": "security-user",
        "password_hash": password_hash.hash("DevSecOps@123"),
        "role": "analyst",
    },
    "admin-user": {
        "username": "admin-user",
        "password_hash": password_hash.hash("AdminPass@123"),
        "role": "admin",
    },
}


def get_user(username: str):
    return USERS.get(username)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)