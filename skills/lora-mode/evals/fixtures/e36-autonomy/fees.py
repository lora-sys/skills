from decimal import Decimal


def parse_amount(raw):
    value = (raw or "").strip()
    if value.startswith("$"):
        value = value[1:]
    return Decimal(value or "0")


def total_amounts(lines):
    return sum((parse_amount(line) for line in lines), Decimal("0"))
