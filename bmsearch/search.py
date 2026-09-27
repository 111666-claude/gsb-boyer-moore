"""Boyer-Moore 搜索（坏字符右移 + 重叠匹配）。只用标准库。"""


class SearchError(Exception):
    """输入不合法。"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def build_shift_table(pattern):
    """坏字符右移表：只记录匹配位置之前出现的下标，最后一位不进表。"""
    table = {}
    for index, char in enumerate(pattern[:-1]):
        table[char] = index
    return table


def search(text, pattern):
    """返回命中位置（升序，含重叠）与字符比较次数。"""
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
            # 命中后只右移 1 位，保留重叠匹配
            index += 1
            continue
        # 错位字符在表中对齐其最后出现位置；不在表中（视为下标 -1）则整段越过它
        shift = offset - table.get(text[index + offset], -1)
        index += shift if shift > 0 else 1
    return positions, comparisons
