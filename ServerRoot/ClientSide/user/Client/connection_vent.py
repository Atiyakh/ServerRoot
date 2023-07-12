import time
from request import RequestsPanel
from socket import *
from pathlib import Path
from os import path
import ssl, json
import traceback
import pickle, gzip
from threading import Thread

class ClassifierList(list):
    def __init__(self):
        self.Int = []
        self.Str = []
    def __len__(self, target):
        if target == 'str':
            return len(self.Str)
        elif target == 'int':
            return len(self.Int)
    def append(self, arg):
        try:
            int(arg)
            self.Int.append(arg)
        except:
            self.Str.append(arg)
    def __getitem__(self, index):
        if index == 'int':
            return self.Int.pop(0)
        elif index == 'str':
            return self.Str.pop(0)
        else:
            raise ValueError(
                'The index should be "int" ot "str" only'
            )
class ConnectionHandler:
    default_encoding = 'utf-8'
    class routerSocketWrapper:
        def __recv__(self):
            while True:
                data = b''
                while True:
                    try:
                        datum = self.router.recv(1024)
                    except (ConnectionAbortedError, ConnectionError, ConnectionResetError, error) as e:
                        self.func2(e)
                        self.func1()
                    if datum:
                        data += datum
                    if len(datum) < 1024:
                        break
                if data:
                    self.data_sequence.append(data)
        def recv_(self, routing=False):
            if routing: target = 'int'
            else: target = 'str'
            while True:
                if self.data_sequence.__len__(target) > 0:
                    return self.data_sequence[target]
        def send_(self, data):
            try: self.router.sendall(data)
            except Exception as e:
                self.func2(e)
                self.func1()
        def __init__(self, router, x, y):
            self.data_sequence = ClassifierList()
            self.blocking = False
            self.router = router
            self.func1 = x; self.func2 = y
    def communications(self):
        while True:
            if len(self.wrappedRouterConnection.data_sequence.Str) != 0:
                data = self.wrappedRouterConnection.data_sequence['str'].decode('utf-8')
                function_, connecting_link_id = data.split('|')
                try:
                    encrypted_client_socket = self.createConnection(communication=True, id_=connecting_link_id)
                    try:
                        self.Requests.Communication.__getattribute__(function_)(encrypted_client_socket)
                        encrypted_client_socket.close()
                    except:
                        traceback.print_exc()
                except self.ConnError as e:
                    self.connectionRefused(e)
    def establishSocketActiveConnection(self, request=False):
        try:
            # socket
            host = (self.IP, self.rport)
            routerConnection = socket(AF_INET, SOCK_STREAM)
            # ssl context
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if not self.cert_varification:
                self.context.check_hostname = False
                self.context.verify_mode = ssl.CERT_NONE
            # wrapping with TLS
            wrappedRouterConnection = self.routerSocketWrapper(self.context.wrap_socket(
                sock=routerConnection, 
                server_side=False, 
                do_handshake_on_connect=True, 
                suppress_ragged_eofs=True, 
                server_hostname=self.IP
                ),
                self.establishSocketActiveConnection,
                self.connectionRefused
            )
            wrappedRouterConnection.router.connect(host)
            if request:
                wrappedRouterConnection.router.send(chr(2).encode('utf-8'))
                return wrappedRouterConnection.router
            else:
                wrappedRouterConnection.router.send(chr(1).encode('utf-8'))
                receiving_thread = Thread(target=wrappedRouterConnection.__recv__)
                self.wrappedRouterConnection = wrappedRouterConnection
                receiving_thread.daemon = True
                receiving_thread.start()
        except self.ConnError as e:
            print(e)
            self.connectionRefused(e)
            self.establishSocketActiveConnection()
    def loadProtocols(self, instance_):
        instance_.RecvProto = self.RecvProto; instance_.SendProto = self.SendProto
        instance_.RecvSignal = self.RecvSignal; instance_.SendSignal = self.SendSignal
    def __init__(self, mainclass):
        self.directory = Path(__file__).resolve().parent
        JSON = json.loads(open(path.join(self.directory, 'config.json'), 'r').read())
        mainclass.server = self
        self.IP = JSON['ip']
        self.entity = JSON['entity']
        self.rport = JSON['router_port']
        self.cert_varification = JSON['hostname_varification']
        self.Requests = RequestsPanel()
        self.loadProtocols(self.Requests)
        self.loadProtocols(self.Requests.Communication)
        self.ConnError = (
            ConnectionError, ConnectionRefusedError, error,
            ConnectionResetError, ConnectionAbortedError, 
            )
        self.establishSocketActiveConnection()
        if 'connectionRefused' in dir(mainclass):
            if type(mainclass.connectionRefused).__name__ == 'function':
                self.connectionRefused = mainclass.connectionRefused
        com_thread = Thread(target=self.communications)
        com_thread.daemon = True
        com_thread.start()
    def PostRequest(self, req, data):
        try:
            encrypted_client_socket = self.createConnection()
            if encrypted_client_socket:
                encrypted_client_socket.send(req.encode('utf-8'))
                if int(encrypted_client_socket.recv(1)):
                    try: 
                        response = self.Requests.__getattribute__(req)(encrypted_client_socket, data)
                        encrypted_client_socket.close(); return response
                    except:
                        traceback.print_exc()
                else: raise ConnectionError("The request you posted is not defined")
            else:
                ConnectionError("Cannot post your request")
        except self.ConnError as e:
            self.connectionRefused(e)
    def connectionRefused(self, err):
        traceback.print_exc()
    def createConnection(self, communication=False, id_=None):
        try:
            encrypted_client_socket = self.establishSocketActiveConnection(request=True)
            addr = encrypted_client_socket.getsockname()
            self.wrappedRouterConnection.send_(f'0|{addr}'.encode('utf-8'))
            self.wrappedRouterConnection.recv_(routing=True)
            encrypted_client_socket.recv(1)
            if communication:
                encrypted_client_socket.send(f"{self.entity}|{1}".encode('utf-8'))
                encrypted_client_socket.recv(1)
                encrypted_client_socket.send(str(id_).encode('utf-8'))
                return encrypted_client_socket
            else:
                encrypted_client_socket.send(f"{self.entity}|{0}".encode('utf-8'))
            code = int(encrypted_client_socket.recv(1))
            if code == 1:
                return encrypted_client_socket
            else:return False
        except (self.ConnError + (ValueError, )) as e:
            self.connectionRefused(e)
            self.createConnection()
    def SendProto(self, conn, d, compress=True, encoding=default_encoding):
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
                conn.send(len(Data).__str__().encode(encoding))
                conn.recv(1)
                conn.sendall(Data)
                conn.recv(1)
            except (ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e:
                raise ConnectionError('SendingError: ' + str(e))
            return 0
        else:
            raise ValueError(
                '[SERVER][PROTOCOL] Use `SendSignal` to transfer a numerical value'
                )
    def RecvProto(self, conn, buffersize=1024, dump=True, decompress=True, encoding=default_encoding):
        Data = b''
        try:
            length = int(conn.recv(1024))
            conn.send(b'0')
            while True:
                Data += conn.recv(buffersize)
                if len(Data) == length: break
            conn.send(b'0')
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
    def RecvSignal(self, conn, encoding=default_encoding):
        try:
            msg = conn.recv(1024)
        except (ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e:
            raise ConnectionError('SignalReceivingError: ' + str(e))
        return int(msg.decode(encoding))
    def SendSignal(self, conn, num, encoding=default_encoding):
        if isinstance(num, int):
            try:
                conn.send(num.__str__().encode(encoding))
            except(ConnectionAbortedError, ConnectionError, ConnectionResetError, socket.error) as e: 
                raise ConnectionError('SignalSendingError: ' + str(e)) 
        else:
            raise TypeError(f'Signal should be an intger not {type(num)}')
