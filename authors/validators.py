
import re

from rest_framework.exceptions import ValidationError

def character_validator(string):
    match = re.search(r"\W", string)
    if match:
        raise ValidationError("invalid character found", code="invalid")
    return string
