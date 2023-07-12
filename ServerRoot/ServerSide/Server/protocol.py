import socket, traceback
import gzip, asyncio
import pickle, time

default_encoding = 'utf-8'

# Connection Tools:
#  conn should be "AsyncStreamObject"
async def SendProto(conn, d, compress=True, encoding=default_encoding):
    if type(d).__name__ not in ('int', 'float'):
        try:
            data = pickle.dumps(d)
        except pickle.PicklingError as e:
            raise ValueError('SerializationError: ' + str(e))
        if compress:
            try:
                Data = gzip.compress(data)
            except IOError as e:
                raise ValueError('CompressingError: ' + str(e))
        else: Data = data
        try:
            await conn.send(len(Data).__str__().encode(encoding))
            await conn.recv(1)
            await conn.send(Data)
            await conn.recv(1)
        except (ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e:
            raise ConnectionError('SendingError: ' + str(e))
        return 0
    else:
        raise ValueError(
            '[SERVER][PROTOCOL] Use `SendSignal` to transfer a numerical value'
            )
async def RecvProto(conn, buffersize=1024, dump=True, decompress=True, encoding=default_encoding):
    Data = b''
    try:
        length = int(await conn.recv(1024))
        await conn.send(b'0')
        while True:
            Data += await conn.recv(buffersize)
            if len(Data) == length: break
        await conn.send(b'0')
    except (ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e:
        raise ConnectionError('ReceivingError: ' + str(e))
    if decompress:
        try:
            data = gzip.decompress(Data)
        except IOError as e:
            raise ValueError('DecompressingError' + str(e))
    else: data = Data
    try:
        d = pickle.loads(data)
    except pickle.UnpicklingError as e:
        raise ValueError('DeserializationError: ' + str(e))
    if dump: return d
    else: conn.__class__.payload = d
async def RecvSignal(conn, encoding=default_encoding):
    try:
        msg = await conn.recv(1024)
    except (ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e:
        raise ConnectionError('SignalReceivingError: ' + str(e))
    return int(msg.decode(encoding))
async def SendSignal(conn, num, encoding=default_encoding):
    if isinstance(num, int):
        try:
            await conn.send(num.__str__().encode(encoding))
        except(ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e: 
            raise ConnectionError('SignalSendingError: ' + str(e)) 
    else:
        raise TypeError(f'Signal should be an intger not {type(num)}')

class Error_:
    def __init__(self, ex):
        self.exception = ex
    def __str__(self):
        return self.exception
    def __bool__(self):
        return False

class CommunicationConnectionCircle:
    connection = False
    def pass_connection(self, connection):
        self.connection = connection
    async def waiting_for_communication_session(self):
        timer = time.time()
        while True:
            await asyncio.sleep(0.1)
            if self.connection or abs(time.time()-timer) > 5:
                return self.connection

async def Communicate(c, conn, function_):
    try:
        comm_class = CommunicationConnectionCircle()
        await conn.send(f'{function_}|{id(comm_class)}'.encode('utf-8'))
        return await comm_class.waiting_for_communication_session()
    except(ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e: 
        err = Error_(traceback.print_exception())
        return err

class loadConnectionProtocols:
    def __init__(self, server):
        server.SendProto = SendProto
        server.RecvProto = RecvProto
        server.SendSignal = SendSignal
        server.RecvSignal = RecvSignal

def loadProtocols(mainclass, entity):
    entity.Server = mainclass.server
    # load connection protocols
    entity.RecvProto = RecvProto
    entity.SendProto = SendProto
    # load connection signals
    entity.RecvSignal = RecvSignal
    entity.SendSignal = SendSignal
    # database & archive & crypto
    entity.Archive = mainclass.server.archive
    entity.DB = mainclass.server.DB
    for name, table in mainclass.server.DB.all_tables:
        entity.__setattr__(name, table)
    entity.where = mainclass.server.DB.where
    entity.Crypto = mainclass.server.Crypto
    # connections & communication
    entity.Connections = mainclass.server.ConnectionIndex_(mainclass.server.Connections)
    entity.Communicate = Communicate
