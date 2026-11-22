def read_rows(lines):
    return [line.strip() for line in lines if line.strip()]


def _summary_text(count):
    return f"Rows: {count}"


def format_summary(count):
    return _summary_text(count)


def main(lines, summary=False):
    rows = read_rows(lines)
    if summary:
        return format_summary(len(rows))
    return rows
