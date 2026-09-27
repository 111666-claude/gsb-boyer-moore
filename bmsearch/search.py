"""Boyer-Moore 搜索。只用标准库。缺陷：坏字符表把最后一位也算进去，命中后跳过重叠。"""


class SearchError(Exception):
    """输入不合法。缺陷：不带位置信息。"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def build_shift_table(pattern):
    """坏字符右移表。缺陷：把最后一位也记进去了，右移量会偏大。"""
    table = {}
    for index, char in enumerate(pattern):
        table[char] = index
    return table


def search(text, pattern):
    """返回命中位置（升序）与比较次数。缺陷：漏重叠、漏匹配。"""
    if not pattern:
        raise SearchError("模式不能是空串")
    size = len(pattern)
    table = build_shift_table(pattern)
    positions = []
    comparisons = 0
    index = 0
    while index <= len(text) - size:
        offset = size - 1
        while offset >= 0:
            comparisons += 1
            if text[index + offset] != pattern[offset]:
                break
            offset -= 1
        if offset < 0:
            positions.append(index)
            # 缺陷：命中后整段跳过，重叠的匹配全丢掉
            index += size
            continue
        shift = table.get(text[index + offset], size) - offset
        index += shift if shift > 0 else 1
    return positions, comparisons
