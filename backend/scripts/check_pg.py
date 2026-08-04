import os
import psycopg2

os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/knowledge_db')

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute("SELECT version(), current_setting('server_encoding')")
print(cur.fetchone())
cur.close()
conn.close()
