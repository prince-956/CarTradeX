# imports PostgreSQL driver 
# to connect with PostgreSQL database
import psycopg2
from psycopg2.extras import RealDictCursor

# creates and return new database connection
def dbConnection():
    return psycopg2.connect(
        host =  "localhost",
        user = "postgres",
        password = "270115",
        database = "CarTradeX"
    )

# query = SQL query-String
# params = values for placeholders
# fetch = tell function to read/write data (True=read & False=write)
def execute_query(query, params=None, fetch=False):
    conn = None
    cur = None

    try:
        conn = dbConnection()
        cur = conn.cursor(cursor_factory=RealDictCursor)     # cursor = Pointer to DB
        # cursor_factory=RealDictCursor => used to get data in form of list of dictionaries (like [{},{},..])
        # otherwise data comes in form of list of tuples (like [(),(),..])

        cur.execute(query, params)

        data = None
        if fetch:
            data = cur.fetchall()
            return data     # returns list of rows
        else:
            conn.commit()   # commit will save changes(insert, update, delete etc)
    
    except Exception as e:
        print("DataBase Error", e)
        return None
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        # it will free memory and close DB Connection