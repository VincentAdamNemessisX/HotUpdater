from .utiller import DataProcessor


class Writer(DataProcessor):
    instance = None  # 单例模式

    def __new__(cls):
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def write_data(self):
        result = self.process("Write None")
        return f"[Writer v{self.version}]  {result}"


# 创建单例对象
writer = Writer()
