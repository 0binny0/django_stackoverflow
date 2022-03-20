
import re

from rest_framework.exceptions import ValidationError

def character_validator(string):
    match = re.search(r"\W|_{2,}", string)
    if match:
        raise ValidationError("invalid character found", code="invalid")
    return string

def total_digits_validator(string):
    match = re.findall(r"\d", string)
    if match and len(match) > 3:
        raise ValidationError("only up to 3 digits allowed in username")
    return string

def password_char_validator(string):
    pattern1 = re.compile("[<>`':;,.]")
