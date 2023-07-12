from .crypto_vent import AES_Algorithm
from socket import *
import time

class KMS_Connection:
    def Insert(self, id_, key):
        while True:
            if not self.socket_occupied: break
        self.socket_occupied = True; self.KMS.send(b'1')
        self.KMS.send(key); self.KMS.recv(1)
        self.KMS.send(id_.__str__().encode('utf-8'))
        self.KMS.recv(1); self.socket_occupied = False
    def Query(self, id_):
        while True:
            if not self.socket_occupied: break
        self.socket_occupied = True; self.KMS.send(b'2')
        self.KMS.send(id_.__str__().encode('utf-8'))
        key = self.KMS.recv(1024); self.socket_occupied = False
        return key
    def Delete(self, id_):
        while True:
            if not self.socket_occupied: break
        self.socket_occupied = True; self.KMS.send(b'3')
        self.KMS.send(id_.__str__().encode('utf-8'))
        self.KMS.recv(1); self.socket_occupied = False
        return 0
    def __init__(self):
        self.socket_occupied = False
        self.KMS_PORT = 1688
        self.KMS = socket(AF_INET, SOCK_STREAM)
        self.KMS.connect((gethostbyname(gethostname()), self.KMS_PORT))
        print("[SERVER][ARCHIVE] Connected to KMS server")

class Archive:
    def insertFile(self, file_name, content):
        t_stamp = time.time()
        data, key = self.AES.Encrypt(content)
        self.server.DB.Insert('archive', {
            'file_name': file_name,
            'data': data,
            't_stamp': t_stamp
        })
        id_ = self.server.DB.Check('archive', [
            [{'file_name': file_name}, 'AND'],
            [{'data': data}, 'AND'],
            [{'t_stamp': t_stamp}]
        ], fetch=1, columns=['id'])[0][0]
        self.kms_conn.Insert(id_, key)
        return id_
    def readFile(self, id_):
        data = self.server.DB.Check('archive', [[{'id': id_}]], fetch=1, columns=['file_name', 'data'])
        file_name, Bytes = data[0]
        key = self.kms_conn.Query(id_)
        bytes_ = self.AES.Decrypt(key, Bytes)
        return file_name, bytes_
    def deleteFile(self, id):
        self.server.DB.Delete('archive', [{'id': id}])
    def updateFile(self, id, data):
        self.server.DB.Update('archive', {'data': data}, [{'id': id}])
    def __init__(self, server):
        self.AES = AES_Algorithm()
        self.kms_conn = KMS_Connection()
        self.server = server
        server.DB.CreateArchive()
