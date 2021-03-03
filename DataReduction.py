import psycopg2 as psycopg2

conn = psycopg2.connect("dbname=CASAS400 user=postgres password=postgres")
cur = conn.cursor()

'''try:
    cur.execute("ALTER TABLE public.events ADD presence bool")
except psycopg2.DatabaseError as e:
    print(e)'''

cur.execute("select * from public.events")
result = cur.fetchall()
patientOccurence = (result[0])[0]
#for row in result:




cur.close()
conn.commit()
conn.close()
