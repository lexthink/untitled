import random
import string

from django_tenants.utils import schema_exists


def generate_random_schema_name() -> str:
    prefix = "schema_"
    while True:
        suffix = "".join(random.choices(string.digits, k=4))
        name = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        schema_name = f"{prefix}{name}_{suffix}"
        if not schema_exists(schema_name):
            break

    return schema_name
