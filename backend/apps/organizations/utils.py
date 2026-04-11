import secrets
import string

from django_tenants.utils import schema_exists


def generate_random_schema_name() -> str:
    prefix = "schema_"
    while True:
        suffix = "".join(secrets.choice(string.digits) for _ in range(4))
        name = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10)
        )
        schema_name = f"{prefix}{name}_{suffix}"
        if not schema_exists(schema_name):
            break

    return schema_name
