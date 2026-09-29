import os
import pymysql
from dotenv import load_dotenv

load_dotenv()
conn = pymysql.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.environ["DB_NAME"],
    ssl={"ca": os.environ["DB_SSL_CA"]},
)
cur = conn.cursor()
cur.execute("SELECT VERSION()")
print("Connected. MySQL version:", cur.fetchone())
conn.close()