import mysql.connector as sql

def drop_db(host, user, passwd, database):
    try:
        db = sql.connect(
            host = host,
            user = user,
            passwd = passwd
        )
        cur = db.cursor(); cur.execute(f'DROP DATABASE {database}')
        db.commit(); db.close()
    except:
        print(f'[Server][SQL_Database] Cannot delete the previous schema from "{database}"')

def LoadQueries(path):
    # Fitch:
    f = open(path, 'r')
    data = f.read()
    data = data[data.find('/*START*/'):]
    f.close()
    # Slice:
    data = data.replace("/*START*/", '["""')
    data = data.replace("/*END*/", '"""]')
    data = data.replace("/**/", '""","""')
    # Loading & Creating & Returning a list to Encompass the whole thing:
    return eval(data)

def loading_tbls(host, user, passwd, database):
    try:
        db = sql.connect(
            host = host,
            user = user,
            passwd = passwd,
            database = database
        )
        cur = db.cursor()
        failures = []; count = 1
        for query in LoadQueries(R"C:\Users\lenovo\Desktop\server_root\ServerSide\Server\DB_Configurations\structure.sql"):
            try:
                cur.execute(query)
                db.commit()
            except Exception as e: failures.append([query, e, count])
            count += 1

        for i in failures:
            print(f"""\n({i[2]}) [{i[1]}]{i[0]}\n""")
    except:
        print("[Server][SQL_Database] loading tables error!")

def create_db(host, user, passwd, database): ######
    try:
        db = sql.connect(
            host = host,
            user = user,
            passwd = passwd
        )
        cur = db.cursor(); cur.execute(f"CREATE DATABASE {database}")
        db.commit(); db.close()
    except:
        print(f'[Server][SQL_Database] Cannot create the database "{database}"!')
