from .Entities.user import User
from .protocol import loadConnectionProtocols, loadProtocols

class viewsRouting:
    def __init__(self, server):
        self.server = server
        loadConnectionProtocols(server)
        self.user = User(); loadProtocols(self, self.user)
        self.structure = {
            'user': self.user,
        }
