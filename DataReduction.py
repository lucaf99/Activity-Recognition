import psycopg2 as psycopg2

conn = psycopg2.connect("dbname=CASAS400 user=postgres password=postgres")
cur = conn.cursor()

query = "CREATE VIEW events_no_duplicates AS\
        SELECT patient,time,sensor,value FROM\
             (SELECT events.*\
             FROM (SELECT events.*, LAG(sensor) OVER (ORDER BY patient) AS prev_sensor FROM events\
             WHERE sensor LIKE 'm%' AND value='on') events\
        WHERE prev_sensor IS DISTINCT FROM sensor) AS right_info;"

try:
    cur.execute(query)
    print("Eseguito correttamente")
except psycopg2.DataError as e:
    print(e)

cur.close()
conn.commit()
conn.close()
