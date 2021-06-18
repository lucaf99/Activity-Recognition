import psycopg2 as psycopg2

from ImagesCreation import createImages
from DataReduction import reduceData
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

    queryEliminazioneTableSampleImages = "DROP TABLE IF EXISTS sample_images"
    cur.execute(queryEliminazioneTableSampleImages)
    queryEliminazioneTableImagesPatientsForActivity = "DROP TABLE IF EXISTS img_pts_for_activity"
    cur.execute(queryEliminazioneTableImagesPatientsForActivity)
    queryEliminazioneVistaUseObjectsPositions = "DROP VIEW IF EXISTS use_objects_positions"
    cur.execute(queryEliminazioneVistaUseObjectsPositions)
    queryEliminazioneVistaMovPosTempoUseObjectsPositions = "DROP VIEW IF EXISTS movimento_pos_tempo"
    cur.execute(queryEliminazioneVistaMovPosTempoUseObjectsPositions)
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