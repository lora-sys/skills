import sys
from parser import parse_line


def main():
    if len(sys.argv) < 2:
        print("usage: python3 tool.py <file>")
        return 2
    total = 0.0
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += parse_line(line)
    print(f"total: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
