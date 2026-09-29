# Prints each .env line's number, key and value LENGTH only, so no secrets appear.
with open(".env", encoding="utf-8-sig") as f:
    for n, line in enumerate(f, 1):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            print(n, "NO '=' SIGN in line, length", len(line))
            continue
        key, value = line.split("=", 1)
        flags = [c for c in ('#', '$', ' ', '"', "'") if c in value.strip()]
        print(n, key, "length", len(value.strip()), "special chars:", flags)
        