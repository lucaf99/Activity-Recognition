import psycopg2 as psycopg2

from ImagesCreation import createImages
from Tesi.DataReduction import reduceData
from config import config

conn = None

try:
    params = config()
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    print('PostgreSQL database version:')
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(db_version)

    queryEliminazioneVistaFirstSensors = "DROP VIEW IF EXISTS first_sensors"
    cur.execute(queryEliminazioneVistaFirstSensors)
    queryEliminazioneVista = "DROP VIEW IF EXISTS events_no_duplicates "
    cur.execute(queryEliminazioneVista)

    reduceData(cur)  # Funzione riduzione numero dati
    createImages(cur)  # Funzione creazione immagini
    conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')
