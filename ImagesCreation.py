from PIL import Image, ImageDraw


def createImages(cur):
    '''queryVista = "CREATE VIEW sensorDoorMovimentDominio as SELECT x,y,sensor,value \
                 FROM events_no_duplicates JOIN sensor_locations ON sensor_id = sensor \
                 LIMIT 50"

    cur.execute(queryVista)'''



    query = "SELECT x,y\
            FROM  sensorDoorMovimentDominio \
            WHERE value = 'on'"

    xmax = "SELECT MAX(x) FROM sensor_locations"
    ymax = "SELECT MAX(y) FROM sensor_locations"
    cur.execute(xmax)
    x = cur.fetchone()
    cur.execute(ymax)
    y = cur.fetchone()

    cur.execute(query)
    results = cur.fetchall()
    print("Eseguito correttamente")

    image_width = 100
    image_height = 130

    scaling_factor_x = image_width / x[0]
    scaling_factor_y = image_height / y[0]

    im = Image.new('RGB', (image_width, image_height), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    i = 0

    while i < cur.rowcount - 1:
        draw.line((results[i][0] * scaling_factor_x, results[i][1] * scaling_factor_y, results[i + 1][0] *
                   scaling_factor_x, results[i + 1][1] * scaling_factor_y), fill=0)
        i = i + 1

    query2 = "SELECT x,y\
            FROM sensorDoorMovimentDominio\
            WHERE sensor LIKE 'd%' AND value = 'open'"

    cur.execute(query2)
    results = cur.fetchall()
    print("Eseguito correttamente")
    i = 0
    while i < cur.rowcount - 1:
        draw.point((results[i][0] * scaling_factor_x, results[i][1] * scaling_factor_y), (255, 0, 0))
        i = i + 1

    im.show()
