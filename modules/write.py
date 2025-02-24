import os


def write_data(cal_num: int = 12):
    from modules.util import sum_fibonacci  # 修正函数名
    rs = sum_fibonacci(cal_num)
    with open(os.path.abspath("stg/data.txt"), "w") as f:
        f.write(f"Result:  {rs}")  # 添加版本标识
