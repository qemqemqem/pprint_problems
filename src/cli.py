#!/usr/bin/env python3

"""
Pretty prints JSONL files with optional selective output.

Run it like this:

```
python pprint_json.py dev.jsonl -n 1 -p label text -r
```
"""

import argparse
import random
import sys

from parsing import process_file, COMMON_LOCATIONS
from printing import (
    print_text, print_file_output,
    configure_console, set_max_print_len
)
from src.parsing import iterate_over_problems, print_structure


def main() -> None:
    global WIDTH
    description, epilog = __doc__.split("\n\n", 1)
    parser = argparse.ArgumentParser(
        description=description.strip(),
        epilog=epilog.strip(),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    group = parser.add_argument_group("Main Arguments")
    group.add_argument(
        "file",
        nargs="?",
        type=str,
        default=sys.stdin,
        help="The file to process. This may be an S3 location. Defaults to stdin.",
    )
    group.add_argument(
        "-p",
        "--parts",
        nargs="*",
        type=str,
        help=f'Optional list of parts to print. Will attempt to find useful defaults if not specified. Possible values: {list(COMMON_LOCATIONS.keys())}, or any other top level JSONL key. You can use a slash, like "foo/bar" to indicate a nested key like problem["foo"]["bar"].',
    )
    group = parser.add_argument_group("Line Selection")
    group.add_argument("-n", "--number", type=int, help="Number of problems to print (defaults to all)")
    group.add_argument("--start", "-s", type=int, default=0, help="Start at this index (inclusive, 0-indexed).")
    group.add_argument("--search", type=str, help="Only include problems that contain this string in the JSON")
    group.add_argument("-r", "--randomize", action="store_true", help="Randomize the order of the problems")
    group.add_argument(
        "--renumber",
        action="store_true",
        help="This only makes a difference with --randomize. If set, it renumbers problems from 1 to N. Otherwise, it keeps the original indexes.",
    )

    group = parser.add_argument_group("Printing Options")
    group.add_argument("-l", "--line-numbers", action="store_true", help="Print line numbers in the code blocks")
    group.add_argument("-w", "--width", type=int, help=f"Set the console width (defaults to {WIDTH})", default=WIDTH)
    group.add_argument(
        "--structure",
        action="store_true",
        help="Print the structure of the loaded data instead of printing the contents",
    )
    group.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw JSONL data instead of pretty printing it. This ignores the --parts flag.",
    )
    group.add_argument("--max-str-len", type=int, help="Maximum length of strings in raw mode.")

    group = parser.add_argument_group("Filtering")
    group.add_argument(
        "--manual-filter", action="store_true", help="Enter a manual filtering mode to select problems with y/n."
    )
    group.add_argument(
        "--filter-output", type=str, default="output.jsonl", help="Output file for filtered problems. Append-mode."
    )
    group.add_argument(
        "--file-output",
        type=str,
        help='Output file for filtered problems. Defaults to text but will write html if the file name ends with ".html". Overwrites.',
    )

    # group = parser.add_argument_group("Miscellaneous Options")

    args = parser.parse_args()

    configure_console(args)

    if args.max_str_len:
        set_max_print_len(args.max_str_len)

    if args.file == sys.stdin:
        file_contents = process_file(sys.stdin)
    elif args.file.lower().startswith("s3://"):
        raise NotImplementedError("S3 support is not yet implemented.")
    else:
        # Else read local file
        with open(args.file, "r") as file:
            file_contents = process_file(file)

    problems = file_contents
    lines = list(enumerate(problems.rstrip().split("\n")))
    total_num_problems = len(lines)
    print_text(f"Found {total_num_problems} problems")
    if args.randomize:
        random.shuffle(lines)
    if args.search:
        lines = [(num, line) for num, line in lines if args.search in line]
        print_text(f"After searching, found {total_num_problems} problems")
    if args.start:
        lines = lines[args.start :]
    if args.number:
        lines = lines[: args.number]

    if args.structure:
        print_structure(args, lines)

    # The main case, iterate over problems
    else:
        iterate_over_problems(args, lines)

    if args.file_output:
        print_file_output(args)


if __name__ == "__main__":
    main()
