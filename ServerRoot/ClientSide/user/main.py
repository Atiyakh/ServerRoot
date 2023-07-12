from Client.connection_vent import *

class User:
    def __init__(self):
        self.Server = ConnectionHandler(self)
        self.initiate()
    def initiate(self):
        pass

if __name__ == '__main__':
    user = User()
