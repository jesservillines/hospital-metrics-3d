import secrets
import string
import argparse

def generate_password(length=32):
    """Generate a secure password with mixed characters."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Check if password meets complexity requirements
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password

def generate_username(prefix="hospital_metrics", length=8):
    """Generate a unique database username."""
    suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return f"{prefix}_{suffix}"

def generate_db_name(env="prod"):
    """Generate database name."""
    return f"hospital_metrics_{env}_{secrets.token_hex(4)}"

def main():
    parser = argparse.ArgumentParser(description='Generate secure database credentials')
    parser.add_argument('--env', default='prod', help='Environment (prod, staging, etc)')
    args = parser.parse_args()

    username = generate_username()
    password = generate_password()
    db_name = generate_db_name(args.env)

    print("\nGenerated Database Credentials")
    print("=============================")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Database: {db_name}")
    print("\nPostgreSQL Commands")
    print("------------------")
    print(f"CREATE DATABASE {db_name};")
    print(f"CREATE USER {username} WITH PASSWORD '{password}';")
    print(f"ALTER DATABASE {db_name} OWNER TO {username};")
    print(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username};")
    print("\nConnection URL")
    print("--------------")
    print(f"DATABASE_URL=postgresql://{username}:{password}@localhost:5432/{db_name}")
    print("\nEnvironment Variables")
    print("--------------------")
    print(f"DB_USER={username}")
    print(f"DB_PASSWORD={password}")
    print(f"DB_NAME={db_name}")
    print("\nIMPORTANT: Store these credentials securely and never commit them to version control!")

if __name__ == "__main__":
    main()
