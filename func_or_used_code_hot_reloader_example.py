import time
import importlib


def main():
    from modules.write import write_data
    from modules.read import read_data
    write_data()
    print(read_data())


if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)
        write = importlib.import_module("modules.write")
        read = importlib.import_module("modules.read")
        util = importlib.import_module("modules.util")
        module_list = [write, read, util]
        for module in module_list:
            importlib.reload(module)
