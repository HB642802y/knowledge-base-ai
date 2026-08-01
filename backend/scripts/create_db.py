import pg8000.dbapi as pg8000
import sys

def main():
    dbname = 'aiagent'
    user = 'postgres'
    password = 'admin123'
    host = 'localhost'
    port = 5432

    try:
        conn = pg8000.connect(database='postgres', user=user, password=password, host=host, port=port)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (dbname,))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {dbname}")
            print('DB_CREATED')
        else:
            print('DB_EXISTS')
        cur.close()
        conn.close()

    except Exception as e:
        print('ERROR', e)
        sys.exit(1)

if __name__ == '__main__':
    main()