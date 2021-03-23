from datetime import timedelta, datetime
from random import randint

from PIL import Image, ImageDraw
import math


def createImages(cur):

    paziente = int(input('Inserisci il nome del paziente da monitorare: '))
    campione = int(input('Inserisci il numero di campioni da analizzare: '))

    queryVistaAppoggio = "CREATE VIEW first_sensors AS SELECT x, y, (lead(time,1) OVER (order by time) - time) AS \
                         delta_time, value FROM events_no_duplicates JOIN sensor_locations ON sensor_id = sensor \
                         WHERE value in ('on','open') AND patient= {} LIMIT {}".format(paziente, campione)
    cur.execute(queryVistaAppoggio)
    print("first_sensors creata correttamente")

    queryPosizioniTempo = "SELECT * FROM first_sensors"

    xmax = "SELECT MAX(x) FROM sensor_locations"
    ymax = "SELECT MAX(y) FROM sensor_locations"
    cur.execute(xmax)
    x = cur.fetchone()
    cur.execute(ymax)
    y = cur.fetchone()
    cur.execute(queryPosizioniTempo)
    posizioniTempoRisultati = cur.fetchall()
    print("Query che seleziona i dati di interesse eseguita correttamente")

    row_query = cur.rowcount

    image_width = 100
    image_height = 130

    scaling_factor_x = image_width / x[0]
    scaling_factor_y = image_height / y[0]

    im = Image.new('RGB', (image_width, image_height), (200, 200, 200))
    draw = ImageDraw.Draw(im)

    i = 0

    velocita = 0
    green = 39
    secondiPazienteFermo = 2  # 2 come esempio, ma può essere cambiato

    while i < row_query - 1:

        # Linee del movimento (viene segnata anche la velocità con tonalità di verde diverse)

        if i > 0:
            velocitaPrecedente = velocita
            velocita = math.sqrt(
                math.pow(posizioniTempoRisultati[i][0] - posizioniTempoRisultati[i - 1][0], 2) + math.pow(
                    posizioniTempoRisultati[i][1] - posizioniTempoRisultati[i - 1][1], 2)) / \
                       posizioniTempoRisultati[i - 1][2].total_seconds()
            if velocita > velocitaPrecedente:
                green += 50
            else:
                if velocita == velocitaPrecedente:
                    break
                else:
                    green -= 50

        draw.line((posizioniTempoRisultati[i][0] * scaling_factor_x, posizioniTempoRisultati[i][1] * scaling_factor_y,
                   posizioniTempoRisultati[i + 1][0] *
                   scaling_factor_x, posizioniTempoRisultati[i + 1][1] * scaling_factor_y), fill=(11, green, 184))

        # Punti in cui stanno fermi
        if posizioniTempoRisultati[i][2] > timedelta(days=0, seconds=secondiPazienteFermo, microseconds=0):
            draw.point(
                (posizioniTempoRisultati[i][0] * scaling_factor_x, posizioniTempoRisultati[i][1] * scaling_factor_y),
                fill=(245, 66, 66))

        i = i + 1

    queryDoor = "SELECT x,y\
            FROM  first_sensors\
            WHERE value = 'open'"

    cur.execute(queryDoor)
    results = cur.fetchall()
    print("Query delle porte eseguita correttamente")
    i = 0
    while i < cur.rowcount:
        draw.point((results[i][0] * scaling_factor_x, results[i][1] * scaling_factor_y), (255, 255, 0))
        i = i + 1

    im.show()