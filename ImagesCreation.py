from PIL import Image, ImageDraw


def createImages(cur):
    query = "SELECT x,y\
            FROM events_no_duplicates JOIN sensor_locations ON sensor_id = sensor\
            LIMIT 10;"

    xmax = "SELECT MAX(x) FROM sensor_locations"
    ymax = "SELECT MAX(y) FROM sensor_locations"
    cur.execute(xmax)
    x = cur.fetchone()
    cur.execute(ymax)
    y = cur.fetchone()

    cur.execute(query)
    results = cur.fetchall()
    print("Eseguito correttamente")

    im = Image.new('RGB', (int(x[0]+1), int(y[0]+1)), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    i = 0
    while i < cur.rowcount - 1:
        draw.line((results[i][0], results[i][1], results[i + 1][0], results[i + 1][1]), fill=0)
        i = i + 1
    im.show()