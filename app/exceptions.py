class ModelError(Exception): 
    def __init__(self, msg):
        self.msg = msg


class ModelNotFound(ModelError):
    def __init__(self, model_id, msg=None):
        self.model_id = model_id
        super().__init__(self, msg)


class RegistrationFailed(ModelError):
    def __init__(self, model_id, msg=None):
        self.model_id = model_id
        super.__init__(self, msg)


class TokenError(Exception):
    def __init__(self, msg):
        self.msg = msg

class TokenNotFound(Exception):
    def __init__(self, token, msg=None):
        self.token = token
        super().__init__(msg)