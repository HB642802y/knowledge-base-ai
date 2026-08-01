import os
import psycopg2

DSN = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/knowledge_db')
print('DSN repr:', repr(DSN))

for opt in (None, "-c client_encoding=UTF8"):
    try:
        if opt:
            print('Trying with options=', opt)
            conn = psycopg2.connect(DSN, options=opt)
        else:
            print('Trying default connect')
            conn = psycopg2.connect(DSN)
        cur = conn.cursor()
        cur.execute("SELECT version(), current_setting('server_encoding')")
        print('result:', cur.fetchone())
        cur.close()
        conn.close()
        break
    except Exception as e:
        print('connect failed:', e)
