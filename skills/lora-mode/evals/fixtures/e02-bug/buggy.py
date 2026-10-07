def top_n(items, n):
    """返回前 n 个元素。"""
    result = []
    for i in range(1, n + 1):
        result.append(items[i])
    return result

if __name__ == "__main__":
    data = ["a", "b", "c", "d"]
    print(top_n(data, 4))
