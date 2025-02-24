import time
import importlib
from types import ModuleType


class HotReloader:
    def __init__(self, modules: list[str] = None):
        self.modules = modules or []
        self.class_registry = {}

    @staticmethod
    def safe_reload(module_name: str) -> ModuleType:
        """安全重载模块"""
        module = importlib.import_module(module_name)
        return importlib.reload(module)

    def update_classes(self):
        """更新类引用并迁移实例"""
        # 按依赖顺序重载
        utiller = self.safe_reload("modules.utiller")
        writer = self.safe_reload("modules.writer")
        reader = self.safe_reload("modules.reader")

        # 获取新类引用
        NewWriter = writer.Writer
        NewReader = reader.Reader

        # # 迁移单例实例
        if hasattr(writer, 'writer'):
            old_writer = writer.writer
            new_writer = NewWriter.__new__(NewWriter)
            new_writer.__dict__.update(old_writer.__dict__)
            writer.writer = new_writer

            # 更新类注册表
        self.class_registry.update({
            'Writer': NewWriter,
            'Reader': NewReader,
            'DataProcessor': utiller.DataProcessor
        })


def main(reloader: HotReloader):
    # 动态获取最新类引用
    Writer = reloader.class_registry['Writer']
    Reader = reloader.class_registry['Reader']

    # 每次创建新实例（演示用，实际生产环境需根据需求设计）
    writer = Writer()
    reader = Reader()

    # 执行操作
    print(writer.write_data())
    print(reader.read_data())
    print(f"Current Processor Version: {writer.version}\n")


if __name__ == "__main__":
    reloader = HotReloader(["modules.utiller", "modules.writer", "modules.reader"])
    reloader.update_classes()  # 初始加载

    while True:
        main(reloader)
        time.sleep(3)

        # 执行热更新
        print("\n--- Reloading modules ---")
        reloader.update_classes()
