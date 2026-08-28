from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


# Demo user for the authentication flow.
# The plaintext password is used only to generate the hash.
DEMO_USERNAME = "security-user"
DEMO_PASSWORD_HASH = password_hash.hash("DevSecOps@123")