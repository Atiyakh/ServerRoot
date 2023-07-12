import mysql.connector as sql

class MySql_Database:
    def InitiateDataBase(self): # DONE
        self.db = sql.connect(
            host = "localhost",
            user = "root",
            passwd = "ROOT",
            database = self.database
        )
        cur = self.db.cursor()
        cur.execute("SHOW TABLES")
        self.names = cur.fetchall()
        cur.close()

    def Insert(self, table, data): # DONE
        print(f"[SERVER][SQL-DATABASE] (Insert) Has been applied:[{table}]")
        # Extract:
        key = (str(list(data.keys())).replace('"', '')).replace("'", '')
        val = list(data.values())
        # Execute:
        cur = self.db.cursor()
        cur.execute(f'''INSERT INTO {table} ({key[1:-1]})\nVALUES ({("%s,"*len(val))[:-1]});''', tuple(val))
        self.db.commit()
        cur.close()

    def Update(self, table, data, where=None): # DONE
        print(f"[SERVER][SQL-DATABASE] (Update) Has been applied:[{table}]")
        # Set
        S = 'SET'; params = []
        for key in data:
            val = data[key]; params.append(val)
            S+=f" {key}=%s,"
        # Where
        S = S[:-1]; W = ''
        if where:
            W = 'WHERE'
            for chunk in where:
                if chunk == where[-1]:
                    data_ = chunk[0]
                    key = list(data_)[0]; val = data_[key]
                    W+=f" {key}=%s"; params.append(val)
                else:
                    data_, operator = chunk
                    key = list(data_)[0]; val = data_[key]
                    W+=f" {key}=%s {operator}"; params.append(val)
        query = f"""UPDATE {table}\n{S}\n{W}"""
        cur = self.db.cursor()
        cur.execute(query, tuple(params))
        self.db.commit(); cur.close()

    def Delete(self, table, where=None): # DONE
        print(f"[SERVER][SQL-DATABASE] (Delete) Has been applied:[{table}]")
        # Extract:
        W = ''; params = []
        if where:
            W = 'WHERE'
            for chunk in where:
                if chunk == where[-1]:
                    data = chunk[0]
                    key = list(data)[0]; val = data[key]
                    W+=f" {key}=%s"; params.append(val)
                else:
                    data, operator = chunk
                    key = list(data)[0]; val = data[key]
                    W+=f" {key}=%s {operator}"; params.append(val)
        # Execute:
        cur = self.db.cursor()
        cur.execute(f'''DELETE FROM {table}\n{W};''', tuple(params))
        self.db.commit(); cur.close()

    def Close(self): # DONE
        self.DB.close()

    def Check(self, table, where=None, fetch=None, columns=['*']): # DONE
        print(f"[SERVER][SQL-DATABASE] (Check) Has been applied:[{table} :: {fetch}]")
        # Extrect:
        W = ''; params = []
        if where:
            W ='WHERE'
            for chunk in where:
                if chunk == where[-1]:
                    data = chunk[0]
                    key = list(data)[0]; val = data[key]
                    W+=f" {key}=%s"; params.append(val)
                else:
                    data, operator = chunk
                    key = list(data)[0]; val = data[key]
                    W+=f" {key}=%s {operator}"; params.append(val)
        if isinstance(fetch, int):
            L = f'LIMIT {fetch}'
        elif fetch == '*':
            L = ''
        else: L = 'LIMIT 0'
        cur = self.db.cursor(buffered=True)
        cur.execute(f"""SELECT {str(columns)[1:-1].replace('"', '').replace("'", '')} FROM {table}\n{W}\n{L};""", tuple(params))
        self.db.commit()
        if fetch: response = cur.fetchall(); cur.close(); return response 
        else: response = bool(cur.fetchone()); cur.fetchall(); cur.close(); return response

    def CreateArchive(self):
        if ('archive',) not in self.names:
            cur = self.db.cursor()
            cur.execute("""
CREATE TABLE archive(
    id INT AUTO_INCREMENT,
    file_name VARCHAR(150),
    t_stamp VARCHAR(30),
    data MEDIUMBLOB,
    PRIMARY KEY (id)
);"""); cur.close()
    def __init__(self, database):
        self.database = database
        self.InitiateDataBase()
