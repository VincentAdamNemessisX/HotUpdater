# 初始版本（注意修正拼写）
def sum_fibonacci(n: int):
    """计算前n项斐波那契数列和"""
    a, b = 0, 1
    total = 0 
    for _ in range(n):
        total += a 
        a, b = b, a + b 
    return total * 2
