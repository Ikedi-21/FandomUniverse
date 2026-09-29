import os
from dotenv import load_dotenv

load_dotenv()
pw = os.environ["DB_PASSWORD"]
print("length:", len(pw))
print("is the placeholder:", "REVEAL" in pw.upper() or "CLICK" in pw.upper())
print("starts with AVNS_:", pw.startswith("AVNS_"))
print("user:", os.environ["DB_USER"])