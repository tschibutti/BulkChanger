class Command:
    def __init__(self, path, body, api, action, name):
        self.path = path
        self.body = body
        self.api = api
        self.action = action
        self.name = name