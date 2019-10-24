class SSLprofile:
    def __init__(self, name):
        self.name = name


    def persist(self, filename):
        ''' persist connections to file '''