class DataProcessor:
    """会被热更新的基类"""
    version = 1.0  # 用于演示版本变化

    @staticmethod
    def process(data):
        return f"Base processed: {data}"
