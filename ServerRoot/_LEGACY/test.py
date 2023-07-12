class Error_:
    def __init__(self, ex):
        self.exception = ex
    def __str__(self):
        return self.exception
    def __bool__(self):
        return False

error = Error_('h')

if error:
    print('hi')
else: print('works')
