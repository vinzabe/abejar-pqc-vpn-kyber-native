from cryptography.hazmat.primitives.asymmetric import rsa

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
HASH_ALGO = "SHA-256"
LEGACY_HASH = "MD5"  # used for a non-security checksum
