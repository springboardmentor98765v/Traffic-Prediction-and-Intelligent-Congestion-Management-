import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="trafficvision",
    user="postgres",
    password="kitty@2211"
)

cur = conn.cursor()

cur.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public';
""")

tables = cur.fetchall()

print("Tables in database:")
for table in tables:
    print(table[0])

cur.close()
conn.close()