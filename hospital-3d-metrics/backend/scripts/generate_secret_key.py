import secrets
import base64

def generate_secret_key(length=32):
    """Generate a secure secret key using secrets module."""
    # Generate random bytes
    random_bytes = secrets.token_bytes(length)
    # Convert to URL-safe base64 and remove padding
    return base64.urlsafe_b64encode(random_bytes).decode().rstrip('=')

if __name__ == "__main__":
    # Generate a 32-byte (256-bit) key
    secret_key = generate_secret_key(32)
    print("\nGenerated SECRET_KEY:")
    print("--------------------")
    print(secret_key)
    print("\nAdd this to your .env.production file as:")
    print(f'SECRET_KEY="{secret_key}"')
    print("\nMake sure to keep this key secure and never commit it to version control!")
