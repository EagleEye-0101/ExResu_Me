"""Phone formatting and validation with country codes."""

import re

try:
    import phonenumbers
except ImportError:
    phonenumbers = None  # type: ignore


def format_phone_display(country_code: str, national: str) -> str:
    cc = (country_code or "+1").strip()
    if not cc.startswith("+"):
        cc = f"+{cc}"
    num = re.sub(r"[^\d]", "", national or "")
    if not num:
        return cc
    if phonenumbers:
        try:
            parsed = phonenumbers.parse(f"{cc}{num}", None)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except Exception:
            pass
    return f"{cc} {num}"


def validate_phone(country_code: str, national: str) -> tuple[bool, str]:
    cc = (country_code or "").strip()
    num = re.sub(r"[^\d]", "", national or "")
    if not cc:
        return False, "Country code is required"
    if not cc.startswith("+"):
        cc = f"+{cc}"
    if len(num) < 7:
        return False, "Phone number is too short"
    if len(num) > 15:
        return False, "Phone number is too long"
    if phonenumbers:
        try:
            parsed = phonenumbers.parse(f"{cc}{num}", None)
            if phonenumbers.is_valid_number(parsed):
                return True, ""
            return False, "Invalid phone number for selected country"
        except Exception:
            return False, "Invalid phone number format"
    if re.match(r"^\+?\d{1,4}$", cc) and 7 <= len(num) <= 15:
        return True, ""
    return False, "Invalid phone number"
