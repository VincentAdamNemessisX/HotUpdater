import os

import modules.util as util  # 修正函数名


def write_data(cal_num: int = 11):
    rs = util.sum_fibonacci(cal_num)
    with open(os.path.abspath("stg/data.txt"), "w") as f:
        f.write(f"Result:  {rs}")  # 添加版本标识
