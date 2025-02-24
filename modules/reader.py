from .utiller import DataProcessor


class Reader(DataProcessor):
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            super().__init__()
            self.cache = []
            self._initialized = True

    def read_data(self):
        result = self.process("Read  None")
        return f"[Reader v{self.version}]  {result}"
