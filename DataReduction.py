def reduceData(cur):
    query = "CREATE VIEW events_no_duplicates AS\
            SELECT patient,time,sensor,value FROM\
                 (SELECT events.*\
                 FROM (SELECT events.*, LAG(sensor) OVER (ORDER BY patient) AS prev_sensor FROM events\
                 WHERE sensor LIKE 'm%' AND value='on') events\
            WHERE prev_sensor IS DISTINCT FROM sensor) AS right_info;"

    cur.execute(query)
    print("Eseguito correttamente")
