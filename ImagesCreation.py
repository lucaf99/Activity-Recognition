import math
from datetime import timedelta
from decimal import Decimal

from PIL import Image, ImageDraw


# piano terra (nella mappa è quello a destra)
def createImages(cur):
    # Massimo valore x e y per calcolo fattore di scala
    xmax = "SELECT MAX(x) FROM sensor_locations"
    ymax = "SELECT MAX(y) FROM sensor_locations"
    cur.execute(xmax)
    x = cur.fetchone()
    cur.execute(ymax)
    y = cur.fetchone()

    # Variabili immagine e altre
    image_width = 100
    image_height = 130
    scaling_factor_x = image_width / x[0]
    scaling_factor_y = image_height / y[0]

    velocita = 0
    green = 39
    secondiPazienteFermo = 2  # 2 come esempio, ma può essere cambiato

    # first_sensors
    queryVistaAppoggio = "CREATE VIEW first_sensors AS SELECT * FROM events_no_duplicates \
                         WHERE value in ('on','open','present') and patient in  \
                        (select distinct person_id from persons where diagnosis in (3,4,8)) \
                         ORDER BY patient, time;"
    cur.execute(queryVistaAppoggio)
    print("first_sensors creata correttamente")

    # movimento_pos_tempo Creazione vista
    vistaPosizioniTempo = "CREATE VIEW movimento_pos_tempo AS SELECT x, y, (lead(time,1) OVER (order by time) - time) AS \
                         delta_time, value, sensor, patient,time FROM first_sensors JOIN sensor_locations ON sensor_id = sensor\
                         WHERE floor = 0"
    cur.execute(vistaPosizioniTempo)
    print("movimento_pos_tempo creata correttamente")

    queryPosizioniOggettiMovimento = "CREATE VIEW use_objects_positions AS \
                                                        SELECT patient,sensor,prev_sensor, x, y, time \
                                                        FROM (SELECT first_sensors.*, LAG(sensor) OVER (ORDER BY patient) \
                                                        AS prev_sensor FROM first_sensors) first_sensors \
                                                        JOIN sensor_locations ON prev_sensor = sensor_id \
                                                        WHERE (prev_sensor LIKE 'm%' OR prev_sensor LIKE 'd%') \
                                                        AND value = 'present' AND floor=0"

    cur.execute(queryPosizioniOggettiMovimento)

    print("queryPosizioniOggettiMovimento creata correttamente")

    queryAttività = "SELECT * FROM activities WHERE patient in  \
            (select distinct person_id from persons where diagnosis in (3, 4, 8))"
    cur.execute(queryAttività)

    attività = cur.fetchall()

    n_attività = cur.rowcount

    start = 0
    while start < n_attività:

        # INIZIALIZZAZIONE IMMAGINE
        im = Image.new('RGB', (image_width, image_height), (200, 200, 200))
        draw = ImageDraw.Draw(im)

        # SEZIONE DISEGNO MOVIMENTI
        queryPosizioniTempo = "SELECT * FROM movimento_pos_tempo \
                              WHERE patient = {} AND time between '{}' \
                              AND '{}' AND value in ('on','open');".format(attività[start][0], attività[start][2],
                                                                           attività[start][3])

        cur.execute(queryPosizioniTempo)
        posizioniTempoRisultati = cur.fetchall()
        row_query = cur.rowcount

        i = 0
        while i < row_query - 1:

            # Linee del movimento (viene segnata anche la velocità con tonalità di verde diverse)

            if i > 0:
                velocitaPrecedente = velocita
                secondiVelocita = posizioniTempoRisultati[i - 1][2].total_seconds()
                if secondiVelocita == 0:
                    secondiVelocita = 1
                velocita = math.sqrt(
                    math.pow(posizioniTempoRisultati[i][0] - posizioniTempoRisultati[i - 1][0], 2) + math.pow(
                        posizioniTempoRisultati[i][1] - posizioniTempoRisultati[i - 1][1], 2)) / \
                           secondiVelocita
                if velocita > velocitaPrecedente:
                    green += 50
                else:
                    if not velocita == velocitaPrecedente:
                        green -= 50

            draw.line(
                (posizioniTempoRisultati[i][0] * scaling_factor_x, posizioniTempoRisultati[i][1] * scaling_factor_y,
                 posizioniTempoRisultati[i + 1][0] *
                 scaling_factor_x, posizioniTempoRisultati[i + 1][1] * scaling_factor_y), fill=(11, green, 184))

            # Punti in cui stanno fermi
            if posizioniTempoRisultati[i][2] > timedelta(days=0, seconds=secondiPazienteFermo, microseconds=0):
                draw.point(
                    (
                        posizioniTempoRisultati[i][0] * scaling_factor_x,
                        posizioniTempoRisultati[i][1] * scaling_factor_y),
                    fill=(245, 66, 66))
            i = i + 1

        print("***Movimenti tracciati***")

        # SEZIONE DISEGNO PORTE
        queryDoor = "SELECT x,y\
                    FROM movimento_pos_tempo \
                    WHERE patient = {} AND time between '{}' \
                              AND '{}' AND value = 'open';".format(attività[start][0], attività[start][2],
                                                                           attività[start][3])

        cur.execute(queryDoor)
        results = cur.fetchall()
        j = 0
        while j < cur.rowcount:
            draw.point((results[j][0] * scaling_factor_x, results[j][1] * scaling_factor_y), (255, 255, 0))
            j = j + 1

        print("***Porte tracciate***")

        #SEZIONE DISEGNO OGGETTI
        queryOggetti = "SELECT *\
                        FROM use_objects_positions \
                        WHERE patient = {} AND time between '{}' \
                        AND '{}';".format(attività[start][0], attività[start][2],
                                           attività[start][3])

        cur.execute(queryOggetti)
        resultsObjects = cur.fetchall()

        # Ci sono solo 4 sensori oggetti che vengono usati (per vederli fare select distinct sensor from used_objects;), quindi l'array di colori sarà di dimensione 4
        arrayColori = [(36, 173, 9), (237, 123, 17), (242, 0, 255),
                       (237, 147, 186)]  # 0 - i001 (verde); 1 - i002 (arancione); 2 - i006 (fucsia); 3 - i010 (rosa)

        k = 0
        while k < cur.rowcount:

            if resultsObjects[k][0] == "i001":
                draw.point(
                    ((resultsObjects[k][2] + Decimal(-0.2)) * scaling_factor_x,
                     (resultsObjects[k][3]) * scaling_factor_y),
                    arrayColori[0])
            if resultsObjects[k][0] == "i002":
                draw.point(
                    ((resultsObjects[k][2]) * scaling_factor_x,
                     (resultsObjects[k][3] + Decimal(+0.2)) * scaling_factor_y),
                    arrayColori[1])
            if resultsObjects[k][0] == "i006":
                draw.point(
                    ((resultsObjects[k][2] + Decimal(+0.2)) * scaling_factor_x,
                     (resultsObjects[k][3]) * scaling_factor_y),
                    arrayColori[2])
            if resultsObjects[k][0] == "i010":
                draw.point(
                    ((resultsObjects[k][2]) * scaling_factor_x,
                     (resultsObjects[k][3] + Decimal(-0.2)) * scaling_factor_y),
                    arrayColori[3])

            k = k + 1

        print("***Oggetti tracciati***")

        # SEZIONE SALVATAGGIO IMMAGINE
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
        im.save("C:/Users/lucaf/PycharmProjects/Tesi/Tesi/Images/"
            + str(attività[start][0]) + "_"
            + str(attività[start][1]) + "_"
            + str(attività[start][2]).replace(":", ".") + "_"
            + str(attività[start][3]).replace(":", ".") + "_.png")

        print("Immagine " + str(start) + " creata")

        #PASSAGGIO A NUOVA ATTIVITA'
        start = start + 1