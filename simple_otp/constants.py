"""Project-wide constants for simple-otp."""

# PBKDF2 key derivation settings
# OWASP recommendation for PBKDF2-HMAC-SHA256 (2023)
PBKDF2_ITERATIONS = 600_000

# Minimum allowed iterations for security
MIN_PBKDF2_ITERATIONS = 100_000
