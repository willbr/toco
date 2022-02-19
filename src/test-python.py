from rich import print
from rich.markup import escape
from pathlib import Path
from difflib import unified_diff
from toco import CompilationUnit


def read_file(fn):
    with open(fn) as f:
        return [l.strip('\n') for l in f.readlines()]


here = Path(__file__).parent

test_folders = sorted(here.glob("tests/*"))

for fld in test_folders:
    # print(repr(fld))

    in_file = fld.joinpath("in.txt")
    out_file = fld.joinpath("out.txt")

    cu = CompilationUnit(in_file)
    result = cu.render().split('\n')

    try:
        expected_result = read_file(out_file)
    except FileNotFoundError:
        expected_result = []

    if expected_result == []:
        with open(out_file, 'w') as f:
            f.write('\n'.join(result))
            f.write('\n')

    diff = list(unified_diff(expected_result, result))
    if diff:
        print(repr(fld))
        print("expected result:")
        print(expected_result)
        print("result:")
        print(result)
        print("diff")
        print(diff)
        print(repr(fld))
        exit(1)

