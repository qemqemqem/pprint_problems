#!/usr/bin/env python3

"""
Pretty prints JSONL problem files with optional selective output.

Here are some recommended ways to use this script:

1. Search for particular problems:
    python scripts/pprint_problems.py problems.jsonl -r --search "keyword" -b

2. Load a local file:
    python scripts/pprint_problems.py test_problems.jsonl --randomize -n 1 --parts code tests

3. Load a local file with "cat":
    cat problems.jsonl | grep "search_term" | python scripts/pprint_problems.py -n 1 -p code

4. Load and randomize problems:
    python scripts/pprint_problems.py -r -n 1 problems.jsonl

5. Use some arguments to only load a subset:
    python scripts/pprint_problems.py my_problems.jsonl --n 3 --width 100 --line-numbers --randomize

6. Print out the structure:
    python scripts/pprint_problems.py --structure test_data.jsonl

7. Print out the raw JSON:
    python scripts/pprint_problems.py --n 1 --raw problems.jsonl

8. Manually filter problems with y/n on the keyboard:
    python scripts/pprint_problems.py problems.jsonl --manual-filter -p code broken_diff
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

    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest='mode', help='Mode of operation')

    # Create the parser for the "print" command (default behavior)
    print_parser = subparsers.add_parser('print', help='Pretty print JSONL files (default mode)')
    
    # Add all existing arguments to both main parser and print parser for backwards compatibility
    for parser_target in [parser, print_parser]:
        group = parser_target.add_argument_group("Main Arguments")
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

    # Create the parser for the "graph" command
    graph_parser = subparsers.add_parser('graph', help='Create graphs from JSONL files')
    graph_parser.add_argument(
        "--input_file",
        type=str,
        help="Path to the input JSONL file with evaluation results"
    )
    graph_parser.add_argument(
        "--param",
        choices=['all', 'bimodal_discount', 'set_size', 'num_people', 'num_interests', 
                'avg_points', 'think_through', 'percent_chain_of_thought'],
        default='set_size',
        help="Parameter to use for x-axis. Use 'all' to generate graphs for all parameters."
    )
    graph_parser.add_argument(
        "--y_value",
        choices=['dinner_score', 'percentile', 'ranking', 'normalized_score', 
                'rank_normalized_score', 'len_response'],
        default='normalized_score',
        help="Value to use for y-axis"
    )
    graph_parser.add_argument(
        "--display_graph",
        action="store_true",
        default=False,
        help="Whether to display the graph (default: False)"
    )
    graph_parser.add_argument(
        "--use_multiple_colors",
        action="store_true",
        default=True,
        help="Use different colors for each box in the plot (default: True)"
    )

    args = parser.parse_args()

    # Handle the different modes
    if args.mode == 'graph':
        from graphing import main as graph_main
        graph_main()
        return
    
    # Default to print mode
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
