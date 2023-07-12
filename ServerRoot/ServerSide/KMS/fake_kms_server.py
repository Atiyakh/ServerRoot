from base64 import b64decode, b64encode
from sqlite3 import connect
from socket import *
import time

KMS_PORT = 1688

sock = socket(AF_INET, SOCK_STREAM)
sock.bind((gethostbyname(gethostname()), KMS_PORT))

class KMS_Server:
    def HandlingConnection(self):
        try:
            while True:
                code = int(self.sock.recv(1))
                if code == 1: # Insert
                    AES_key = b64encode(self.sock.recv(1024))
                    print(AES_key)
                    self.sock.send(b'0'); id_ = float(self.sock.recv(1024))
                    self.cur.execute(f"""INSERT INTO key VALUES({id_}, "{AES_key}", "{str(time.time())}")""")
                    self.sock.send(b'0')
                    print("[KMS] Iserting new cryptographic key has been implemented")
                elif code == 2: # Query
                    id_ = int(self.sock.recv(1024))
                    self.cur.execute(f"SELECT key FROM key WHERE id={id_};")
                    key = b64decode(self.cur.fetchone()[0])
                    self.sock.send(key)
                    print("[KMS] The server has requested a cryptographic key")
                elif code == 3: # Delete
                    id_ = int(self.sock.recv(1024))
                    self.cur.execute(f"DELETE FROM key WHERE id={id_};")
                    self.sock.send(b'1')
                    print("[KMS] The server has deleted a key")
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError, error):
            self.DB.close(); self.sock.close()
            print('[KMS] Server disconnected...')

    def __init__(self):
        # sql
        self.DB = connect('database.sqlite3')
        self.cur = self.DB.cursor()
        # socket
        while True:
            sock.listen()
            self.sock, addr = sock.accept()
            if addr[0] == gethostbyname(gethostname()): break
            else: self.sock.close()
        self.sock = self.sock
        print('[KMS] Connected to server...')

if __name__ == '__main__':
    while True:
        KMS = KMS_Server()
        KMS.HandlingConnection()
