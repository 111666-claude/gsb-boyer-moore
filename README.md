# boyer-moore

Boyer-Moore 字符串搜索（坏字符右移 + 重叠匹配），只用 Python 标准库。

```
python3 -m bmsearch.cli --text aaaaa --pattern aa
python3 -m bmsearch.cli --text abaa --pattern aa
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **重叠匹配也要报**：`--text aaaaa --pattern aa` 按口径是 `matches=0,1,2,3`，现在因为命中后整段跳过，
  只给 `matches=0,2`。
- **坏字符表只用匹配位置之前出现的下标**：最后一位不能进表。现在把最后一位也记进去，
  `--text abaa --pattern aa` 一个匹配都不给（按口径应给 `matches=2`）。
- 右移量：错位字符在模式里出现过就对齐它最后一次出现的位置，没出现过就整段移过去；右移量至少为 1。
- 输出：`matches=` 是命中的起始下标（升序、逗号分隔，没有命中就是空），`comparisons=` 是字符比较次数。
- 空模式报错；模式比文本长给空结果；文本与模式按码点逐个比较（不做大小写折叠）。
- 不变量：命中集合与「朴素逐位扫描」逐元素一致（含重叠）；同一输入重复运行结果相同。
- 效率：`--text`（400 个 `e` 后接 `abcde`）配 `--pattern abcde` 时，`comparisons` 必须 ≤ 文本长度 405
  （现在给 801，等于逐位退化成两倍文本长度）。
- 规模：10 MB 文本、模式 ≤ 64 个字符，单遍扫描，内存 O(模式长度 + 命中数)。
- 对照自证：随机 2000 组文本/模式，与朴素扫描逐组一致，差异必须为 0。

## 现在的行为

- `search` 命中后只右移 1 位，重叠匹配全部保留（`aaaaa` / `aa` 给 `0,1,2,3`）。
- `build_shift_table` 只记录末位之前的下标；错位字符在表里就对齐其最后出现位置，
  不在表里就整段越过（`offset + 1`），右移量至少为 1（`abaa` / `aa` 给 `2`）。
- 坏字符右移生效后，405 字节那组输入的比较次数降到 205（≤ 文本长度）。

## 计划新增的能力

```
--text 文本     被搜索的文本
--pattern 模式  模式串
```

## 输出

```
matches=0,1,2,3
comparisons=7
```

## 目录

```
bmsearch/search.py   坏字符表与搜索
bmsearch/cli.py      命令行入口
tests/               unittest 用例
```
