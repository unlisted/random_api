class ModelError(Exception): 
    def __init__(self, msg):
        self.msg = msg


class ModelNotFoundError(ModelError):
    def __init__(self, model_id, msg=None):
        self.model_id = model_id
        super().__init__(self, msg)