import psycopg2
import os

conn = psycopg2.connect(os.environ["DATABASE_URL"])

cur = conn.cursor()

cur.execute("select * from color;")
for row in cur:
    print(row)

conn.close()