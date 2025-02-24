# test_module.py  
import os
import time
from modules.hot_reloader import AdvancedHotReloader  # 引用前文实现的热重载系统
from modules import write  # 引用前文实现的业务逻辑

data_path = os.path.abspath("stg/data.txt")


class Test:
    def __init__(self):
        # 初始化基础属性 
        self._setup()

        # 注册到热重载系统 
        reloader.class_registry.setdefault(self.__class__, set()).add(self)

        # 首次执行 
        self.run()

    def _setup(self):
        """初始化非业务相关属性"""
        self.last_run = 0

    @staticmethod
    def run():
        """业务逻辑主入口"""
        try:

            # 核心业务逻辑 
            write.write_data()
            with open(data_path) as f:
                print(f"[{time.ctime()}]  Current output: {f.read()}")

        except Exception as e:
            print(f"业务逻辑异常: {str(e)}")
            time.sleep(1)

        # 初始化热重载系统（需提前配置项目路径）


if __name__ == "__main__":
    # 配置项目根目录
    PROJECT_ROOT = os.path.abspath(".")

    # 初始化系统
    reloader = AdvancedHotReloader(PROJECT_ROOT)
    tester = Test()
    # 注册需要跟踪的类实例
    reloader.class_registry[Test].add(tester)

    # 启动热重载
    reloader.run(interval=0.5)
