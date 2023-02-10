import re

import phonenumbers


def format_phone(number):
    phonematchstring = r"(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
    if re.match(phonematchstring, number) is not None:
        return phonenumbers.format_number(phonenumbers.parse(number, "US"),
                                          phonenumbers.PhoneNumberFormat.NATIONAL)
    else:
        return None
