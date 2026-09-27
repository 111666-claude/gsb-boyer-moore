"""命令行入口：打印所有命中位置与比较次数。"""

import argparse
import sys

from .search import SearchError, search


def build_parser():
    parser = argparse.ArgumentParser(prog="boyer-moore", description="Boyer-Moore 字符串搜索")
    parser.add_argument("--text", help="被搜索的文本")
    parser.add_argument("--pattern", help="模式串")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.text is None or args.pattern is None:
        print("错误：需要 --text 与 --pattern", file=sys.stderr)
        return 2
    try:
        positions, comparisons = search(args.text, args.pattern)
    except SearchError as error:
        print("错误：%s" % error, file=sys.stderr)
        return 1
    print("matches=%s" % ",".join(str(index) for index in positions))
    print("comparisons=%d" % comparisons)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
