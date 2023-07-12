# TCP Server V3:
3/2/2023

import Server
from socket import *
from threading import Thread
from pathlib import Path
import asyncio, ssl
import traceback, os
import ctypes

Thread_ = lambda target, args=[]:Thread(target=target, args=args).start()
cls = lambda: os.system('cls')

class ConnectionIndex(list):
    def __init__(self, d):
        self.addr_conn = d
    def __getitem__(self, param):
        try:
            ip = self.addr_conn[param]
            return ip
        except:
            return False

class TCP_Server:
    # Server Initiators / Server Runner:
    def __init__(self):
        self.Connections = dict()
        self.reqaddr_addr = dict()
        self.ConnectionIndex_ = ConnectionIndex
        self.CA_ApprovedTLS = False
        self.directory = Path(__file__).resolve().parent
        self.defaultKMS = self.directory.joinpath('KMS\\fake_kms_server.py')
        self.var_name_in_globals = None
        for name, value in globals().items():
            if value is self:self.var_name_in_globals = name; break

    def closeConnection(self, writer, addr=None, reqaddr=None, conn=None):
        print(f"[SERVER] Connection {addr} Closed...")
        if addr:
            del self.Connections[str(addr)]
            self.DB.update_conn(conn)
        else:
            del self.reqaddr_addr[str(reqaddr)]
        writer.close()

    class AsyncStreamObject:
        async def send(self, data):
            self.writer.write(data)
            await self.writer.drain()
        async def recv(self, buffer):
            return await self.reader.read(buffer)
        def close(self):
            self.writer.close()
        def __init__(self, writer, reader):
            self.writer = writer
            self.reader = reader

    async def requestHandler(self, reader, writer, router_addr):
        try:
            addr = writer.get_extra_info('peername')
            # Requests routing system V2:
            function = (await reader.read(1024)).decode('utf-8')
            entityHandler = self.viewsRouting.structure[reader.category]
            if function == '' or function == b'':
                self.closeConnection(writer, reqaddr=addr)
            elif function in dir(entityHandler):
                writer.write(b'1')
                await writer.drain()
                conn = self.AsyncStreamObject(
                    writer=writer,
                    reader=reader
                )
                conn.ip = router_addr.__str__()
                try: await entityHandler.__getattribute__(function)(conn)
                except: traceback.print_exc()
            else:
                writer.write(b'0')
                await writer.drain()
            self.closeConnection(writer, reqaddr=addr)
        except (ConnectionAbortedError, ConnectionError, ConnectionResetError, error):
            self.closeConnection(writer, reqaddr=addr)

    async def requests_handler(self, reader, writer):
        try:
            id_ = None
            writer.write(b'0')
            category, status = (await reader.read(4000)).decode('utf-8').split('|')
            if status == '1':
                writer.write(b'0')
                id_ = int((await reader.read(100)).decode('utf-8'))
                conn = self.AsyncStreamObject(
                    writer=writer,
                    reader=reader
                )
                ctypes.cast(id_, ctypes.py_object).value.pass_connection(conn)
            else:
                addr = writer.get_extra_info('peername')
                router_addr = self.reqaddr_addr[str(addr)]
                if category in self.viewsRouting.structure.keys():
                    reader.__class__.category = category
                    writer.write(b'1')
                    await writer.drain()
                    await self.requestHandler(
                        reader, writer, 
                        router_addr
                    )
                else:
                    writer.write(b'0')
                    await writer.drain()
                    writer.close()
        except (ConnectionAbortedError, ConnectionError, ConnectionResetError, error):
            writer.close()

    async def manageIndividual(self, conn, addr):
        self.Connections[str(addr)] = conn
        conn.ip = str(addr)
        code = (await conn.recv(1))
        if code == chr(1).encode('utf-8'):
            while True:
                try:
                    data = (await conn.recv(4000)).decode('utf-8').split('|')
                    if data[0] == '0': # connection authentication & archiving
                        self.reqaddr_addr[data[1]] = str(addr)
                        await conn.send(b'0')
                    else:
                        del self.Connections[str(addr)]
                        print(f'[SERVER][ROUTER] Connection {addr} closed')
                        break
                except (ConnectionAbortedError, ConnectionError, ConnectionResetError, error):
                    self.closeConnection(conn, addr=addr, conn=conn)
                    break
                except Exception as e:
                    traceback.print_exc()
                    break
        elif code == chr(2).encode('utf-8'):
            await self.requests_handler(
                reader=conn.reader,
                writer=conn.writer
            )
        elif code == chr(3).encode('utf-8'):
            id_ = int((await conn.recv(100)))
            await self.requests_handler(
                reader=conn.reader,
                writer=conn.writer,
                id_=id_
            )
        else:
            del self.Connections[str(addr)]
            print(f'[SERVER][ROUTER] Connection {addr} closed')

    def startSocket(self):
        async def run_socket():
            async def handle_client(reader, writer):
                conn = self.AsyncStreamObject(
                    writer=writer,
                    reader=reader
                )
                addr = writer.get_extra_info('peername')
                await self.manageIndividual(conn, addr)

            self.server_stream = await asyncio.start_server(
                handle_client, self.HOST,
                self.PORT, ssl=self.context)

            async with self.server_stream:
                print('[SERVER][STREAM] waiting for incoming connections...')
                await self.server_stream.serve_forever()

        asyncio.run(run_socket())

    def ActiveConsole(self):
        def main():
            print("[SERVER][Console] Active Console  <ON>")
            while True:
                try: exec(input(), globals())
                except Exception as e: print(e)
        Thread_(main)

    def SQL_Database(self, db_name, host, user, passwd):
        self.runKMS()
        self.DB = Server.sql_db(db_name, host, user, passwd)
        self.archive = Server.Archive(self)
        print("[SERVER][ARCHIVE] Archive Environment has been set up...")
        print(f'''[SERVER][SQL-DATABASE] "{db_name}" has been Initiated {str([i for i in self.DB.tablesNames]).replace("'", '')}''')
    def runKMS(self):
        try:
            test = socket(AF_INET, SOCK_STREAM)
            test.bind((gethostbyname(gethostname()), 1688))
            test.close()
            os.startfile(self.KMS_DIR)
        except error as e:
            if e.errno != 10048:
                traceback.print_exc()

    def startTLS(self, key, cer):
        self.CA_ApprovedTLS = True
        self.privatKeyPath = key
        self.certificatePath = cer

    def RunServer(self):
        # generate ssl context
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if self.CA_ApprovedTLS:
            self.context.load_cert_chain(
                certfile=self.certificatePath, 
                keyfile=self.privatKeyPath
            )
        else:
            self.context.load_cert_chain(
                certfile='TLS\\server_certificate.pem', 
                keyfile='TLS\\server_private_key.pem'
            )
        # Server Vars
        self.Crypto = Server.Crytography()
        self.viewsRouting = Server.viewsRouting(self)
        # Server Activation
        self.startSocket()
        print("[SERVER] Server has been successfully Initialized...")

if __name__ == '__main__':
    server = TCP_Server()
    # socket configurations
    server.HOST = gethostbyname(gethostname())
    server.PORT = 80
    # database & archive 
    server.KMS_DIR = server.defaultKMS
    server.SQL_Database(
        db_name='Project_DB_1',
        host='localhost',
        user='ROOT',
        passwd='root'
        )
    server.DB.UpdateSchema()
    # activate server & console
    server.ActiveConsole()
    server.RunServer()
