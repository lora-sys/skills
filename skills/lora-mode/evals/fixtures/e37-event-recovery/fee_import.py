import sys
from pathlib import Path

from fees import total_amounts


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: fee_import.py <amounts-file>", file=sys.stderr)
        return 2

    try:
        lines = Path(argv[0]).read_text(encoding="utf-8").splitlines()
        total = total_amounts(lines)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    print(f"${total:,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
