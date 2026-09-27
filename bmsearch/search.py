"""Boyer-Moore 搜索。只用标准库。"""


class SearchError(Exception):
    """输入不合法。缺陷：不带位置信息。"""

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
    """返回命中位置（升序）与比较次数。重叠匹配也报。"""
    if not pattern:
        raise SearchError("模式不能是空串")
    size = len(pattern)
    if size > len(text):
        return [], 0
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
            index += 1
            continue
        bad = text[index + offset]
        if bad in table:
            shift = offset - table[bad]
        else:
            shift = offset + 1
        index += shift if shift > 0 else 1
    return positions, comparisons
