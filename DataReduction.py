def reduceData(cur):
    cur.execute(
        "ALTER TABLE sensor_locations DROP COLUMN IF EXISTS floor;"
        "ALTER TABLE sensor_locations ADD COLUMN floor smallint;"
        "UPDATE sensor_locations SET floor = 0 WHERE sensor_id IN ('d002', 'm004', 'm005', 'm011', 'e001', 'm012', "
        "'m003', 'm006', 'm010', 'm013', 't001', 'i008', 'i009', 'r002', 'm002', 'm007', 'm009', 'm014', 'd013', "
        "'m008', 'i011', 'i012', 'm001', 'm015', 'm023', 'm016', 'd012', 'd008', 'd009', 'd010', 'r001', 'm022', "
        "'m021', 'm026', 'm025', 'l009', 'm024', 'd001', 'm019', 'm020', 'l011', 'l010', 'm017', 't002', 'm018', "
        "'m051', 'd011', 'd014', 'd015', 'd007', 'i007', 'd016', 'l008');"
        "UPDATE sensor_locations SET floor = 1 WHERE sensor_id NOT IN ('d002', 'm004', 'm005', 'm011', 'e001', 'm012', "
        "'m003', 'm006', 'm010', 'm013', 't001', 'i008', 'i009', 'r002', 'm002', 'm007', 'm009', 'm014', 'd013', "
        "'m008', 'i011', 'i012', 'm001', 'm015', 'm023', 'm016', 'd012', 'd008', 'd009', 'd010', 'r001', 'm022', "
        "'m021', 'm026', 'm025', 'l009', 'm024', 'd001', 'm019', 'm020', 'l011', 'l010', 'm017', 't002', 'm018', "
        "'m051', 'd011', 'd014', 'd015', 'd007', 'i007', 'd016', 'l008');"
    )
    query = "CREATE VIEW events_no_duplicates AS\
            SELECT patient,time,sensor,value FROM\
                 (SELECT events.*\
                 FROM (SELECT events.*, LAG(sensor) OVER (ORDER BY patient) AS prev_sensor FROM events) events\
            WHERE prev_sensor IS DISTINCT FROM sensor) AS right_info;"

    cur.execute(query)
    print("Eseguito correttamente")