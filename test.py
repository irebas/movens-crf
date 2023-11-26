def divide_into_parts(x: int, n: int):
    base_size = x // n
    remainder = x % n
    result = []
    start = 0

    for i in range(n):
        end = start + base_size
        if i < remainder:
            end += 1
        result.append((start, end))
        start = end

    return result
