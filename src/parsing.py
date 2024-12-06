"""
Pretty prints JSONL files with optional selective output.

Run it like this:

```
python pprint_json.py dev.jsonl -n 1 -p label text -r
```
"""

import argparse
import difflib
import json
import random
import sys
from typing import Any
from typing import Dict
from typing import Optional
from typing import TextIO

from printing import print_header_2, print_code, print_text, print_header_3
from printing import print_header_1, print_text, print_code


def process_file(file: TextIO) -> str:
    s = file.read()
    return s


# Common locations in JSONL files for these parts to be found. This attempts to be robust to different naming conventions. "/" indicates a nested key, like problem["foo"]["bar"] as "foo/bar".
COMMON_LOCATIONS: dict[str, list[str]] = {
    "code": ["code", "attempt_module"],  # Note that this is "solution code", and you may want "prompt" or "attempts"
    "broken_code": ["broken_code"],
    "prompt": ["prompt", "question", "problem description", "problem/code_module", "code_module"],
    "tests": ["tests", "problem/test_module", "test_module"],
    "constraints": ["constraints"],
    "background_code": ["background_code", "background"],
    "broken_suggestions": ["broken_suggestions"],
    "tests_pass": ["tests_pass"],
    "tests_error": ["tests_error"],
    "attempts": ["attempts"],
    "answer": ["answer", "resps"],
    "is_correct": ["is_correct", "correct"],
}


def get_nested_value(d: dict, keys: list[str]) -> Any:
    for key in keys:
        if key in d:
            d = d[key]
        else:
            return None
    return d


def build_parts(problem: dict, parts: list[str]) -> dict[str, Any]:
    """
    Tries to robustly find the listed parts, looking in likely places.
    """
    results = {}
    for part in COMMON_LOCATIONS.keys():
        if part in problem:
            results[part] = problem[part]
        else:
            for key in COMMON_LOCATIONS[part]:
                if "/" in key:
                    keys = key.split("/")
                    value = get_nested_value(problem, keys)
                    if value is not None:
                        results[part] = value
                        break
                elif key in problem:
                    results[part] = problem[key]
                    break

    for part in parts:
        if "/" in part:
            keys = part.split("/")
            value = get_nested_value(problem, keys)
            if value is not None:
                results[part] = value
                continue
        if part not in results:
            results[part] = problem.get(part, None)

    return results


def get_all_keys(problem: dict) -> list[str]:
    places = list(problem.keys())
    keys = []
    while places:
        place = places.pop()
        if isinstance(problem[place], dict):
            # Recursion
            keys.extend([place + "/" + key for key in get_all_keys(problem[place])])
        else:
            keys.append(place)
    # Reverse so that the order is preserved
    keys.reverse()
    return keys


def print_problem(orig_problem, parts: Optional[list[str]] = None, print_line_numbers: bool = False) -> None:
    """
    Pretty print a problem, with an option to specify which parts are printed. Uses the `rich` library if installed. It attempts to print code blocks with syntax highlighting, and tests with pass/fail status.
    """
    using_default_parts = False
    if parts is None:
        # parts = ["prompt", "code", "tests", "attempts"]  # TODO This was an old attempt to present a good default
        parts = ["all"]
        using_default_parts = True
    if "all" in parts:
        parts = get_all_keys(orig_problem)
    problem = build_parts(orig_problem, parts=parts)  # This is where we look for alternative locations
    for part in parts:
        if (
            not using_default_parts
            or part in problem
            or (using_default_parts and part == "attempts" and "executed_attempts" in orig_problem)  # Edge case
        ):
            print_header_2(part.capitalize().replace("_", " "))
        # Sometimes the prompt is code-like. This is a heuristic to determine if it is.
        is_code_like = (
            part in problem
            and isinstance(problem[part], str)
            and (
                problem[part].strip().startswith("import")
                or problem[part].strip().startswith("from")
                or problem[part].strip().startswith("def")
            )
        )
        # These are special cases, before we check `part not in problem`
        if part == "broken_diff":
            code = problem["code"]
            broken_code = problem["broken_code"]
            diff = difflib.unified_diff(
                broken_code.splitlines(keepends=True),
                code.splitlines(keepends=True),
                fromfile="broken_code",
                tofile="code",
                lineterm="\n",
                n=3,  # Number of lines of context
            )
            diff_str = "\n".join([line.strip() for line in diff])
            print_code(diff_str, print_line_numbers=print_line_numbers, lexer="diff")
        elif part == "attempts":
            try:
                attempts = orig_problem["executed_attempts"]
                print_text(f"Found {len(attempts)} attempts")
                for i, attempt in enumerate(attempts):
                    print_header_3(f"Attempt {i + 1} Code")
                    attempt_code = attempt["attempt"]["attempt_module"]
                    print_code(attempt_code, print_line_numbers=print_line_numbers)
                    print_header_3(f"Attempt {i + 1} Results")
                    print_code(attempt["execution_result"]["stdout"], print_line_numbers=print_line_numbers)
                    print_header_3(f"Attempt {i + 1} Return Code")
                    rc = attempt["execution_result"]["return_code"]
                    print_text(f'Return code: {rc} ({"success" if rc == 0 else "failure" if rc == 1 else "unknown"})')
            except KeyError as e:
                print_text(f"Error parsing attempts. KeyError: {e}")
                print_text(f"Problem details: {json.dumps(orig_problem)}")
        elif part not in problem:
            if not using_default_parts:
                print_text(f'Part "{part}" not found in problem. Run with --structure to see available parts.')
            continue
        # Specially handle each type of thing
        elif part == "code":
            print_code(problem[part], print_line_numbers=print_line_numbers)
        elif part == "broken_code":
            print_code(problem[part], print_line_numbers=print_line_numbers)
        elif part == "prompt":
            if is_code_like:
                print_code(problem[part], print_line_numbers=print_line_numbers)
            else:
                print_text(problem[part])
        elif part == "tests":
            tests = problem[part]
            if isinstance(tests, str):
                tests = [tests]
            passes = orig_problem["tests_pass"] if "tests_pass" in orig_problem else ["Unk."] * len(tests)
            errors = orig_problem["tests_error"] if "tests_error" in orig_problem else ["Unk."] * len(tests)
            error_texts = (
                orig_problem["tests_error_texts"] if "tests_error_texts" in orig_problem else [""] * len(tests)
            )
            for j in range(len(tests)):
                quote = '"'
                if "tests_pass" in orig_problem or "tests_error" in orig_problem:
                    print_text(
                        f"Test {j + 1}. Passes: [{'blue' if passes[j] else 'red'}]{passes[j]}[/]. Errors: [{'red' if errors[j] else 'blue'}]{errors[j]}[/], {quote + error_texts[j] + quote if errors[j] else ''}"
                    )
                else:
                    print_text(f"Test {j + 1}.")
                print_code(tests[j], lexer="python", print_line_numbers=print_line_numbers)
        elif part == "constraints":
            print_text("\n".join([f" - {c}" for c in problem[part]]))
        elif part == "background":
            print_code(problem[part], print_line_numbers=print_line_numbers)
        elif part == "suggestions":
            print_text("\n".join([f" - {c}" for c in problem[part]]))
        elif part == "broken_suggestions":
            print_text("\n".join([f" - {c}" for c in problem[part]]))
        else:
            # Unknown type fallback
            if not isinstance(problem[part], str):
                print_text(json.dumps(problem[part], indent=4))
            else:
                if is_code_like:
                    print_code(problem[part], print_line_numbers=print_line_numbers)
                else:
                    print_text(problem[part])


def get_type(value: Any) -> str:
    """Get the type of the value as a string."""
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, list):
        return f"list[{get_type(value[0])}]" if value else "list"
    return type(value).__name__


class DataRange:
    """A class to represent a range of data values, for stats printing"""

    def __init__(self):
        self.values = []

    def __str__(self) -> str:
        try:
            if all(isinstance(value, list) for value in self.values):
                # Check this first, because lists aren't hashable
                return f"lengths: {min(len(value) for value in self.values)} to {max(len(value) for value in self.values)}"
            elif len(set(self.values)) <= 3:
                if all(isinstance(value, str) for value in self.values) and any(len(value) > 20 for value in self.values):
                    pass # Do nothing, pass through to next if
                else:
                    # Calculate counts of each value
                    counts = {value: self.values.count(value) for value in set(self.values)}
                    percentages = {value: count / sum(counts.values()) for value, count in counts.items()}
                    return ", ".join([f"{percentages[value] * 100:.0f}% {value}" for value in sorted(counts.keys())])

            # Don't make this elif
            if all(isinstance(value, (int, float)) for value in self.values):
                return f"{min(self.values)} to {max(self.values)}, avg: {sum(self.values) / len(self.values)}"
            elif all(isinstance(value, str) for value in self.values):
                return f"{len(set(self.values))} distinct values, length: {min(len(value) for value in self.values)} to {max(len(value) for value in self.values)}"
            else:
                return f"{len(set(self.values))} distinct values"
        except TypeError:
            # No real fallback
            return ""


def add_to_data_ranges(data: dict[str, Any], keys: list[str], value_stats: dict[str, DataRange]) -> None:
    # Recursive
    for key, value in data.items():
        key_str = "::".join(keys + [key])
        if isinstance(value, dict):
            add_to_data_ranges(value, keys + [key], value_stats)
        else:
            if key_str not in value_stats:
                value_stats[key_str] = DataRange()
            value_stats[key_str].values.append(value)


def get_data_ranges(data: list[dict[str, Any]]) -> dict[str, DataRange]:
    data_ranges = {}
    for item in data:
        add_to_data_ranges(item, [], data_ranges)

    return data_ranges


def print_json_structure(data: Dict[str, Any], indent: int = 1, keys: list[dict] = None, data_ranges: dict[str, DataRange] = None) -> str:
    """Recursively print the structure of a JSON object."""
    if keys is None:
        keys = []
    if data_ranges is None:
        data_ranges = {}
    s = "    " * (indent - 1) + "{\n"
    if "__type" in data:
        s += "    " * indent + f'"__type": {data["__type"]}\n'
    for key, value in data.items():
        data_range = data_ranges.get("::".join(keys + [key]), None)
        data_range_str = f"({data_range.__str__()})" if data_range else ""
        the_type = get_type(value)
        if key == "__type":
            pass
        elif isinstance(value, str):
            s += "    " * indent + f'"{key}": {the_type} ({len(value)} characters) {data_range_str}\n'
        elif isinstance(value, list):
            s += "    " * indent + f'"{key}": {the_type} ({len(value)} items) {data_range_str}\n'
        elif isinstance(value, dict):
            s += "    " * indent + f'"{key}": {the_type} ({len(value)} items) {data_range_str}\n'
        elif isinstance(value, (bool, int, float)):
            s += "    " * indent + f'"{key}": {the_type} {data_range_str}\n'
        else:
            s += "    " * indent + f'"{key}": {the_type} {data_range_str}\n'
        # Recursion!
        if isinstance(value, dict):
            s += print_json_structure(value, indent + 1, keys=keys + [key], data_ranges=data_ranges) + "\n"
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            s += "    " * indent + f"[\n"
            s += print_json_structure(value[0], indent + 2, keys=keys + [key], data_ranges=data_ranges) + "\n"
            s += "    " * (indent + 1) + f"... ({len(value) - 1} more items)\n"
            s += "    " * (indent) + f"]\n"
    return s + "    " * (indent - 1) + "}"


def print_structure(args, lines: list[tuple[int, str]], print_data_ranges: bool = False):
    if print_data_ranges:
        print_header_1(f"JSON Structure (problem {lines[0][0]}), with Data Ranges from {len(lines)} Samples")
    else:
        print_header_1(f"JSON Structure (problem {lines[0][0]})")
    data_ranges = get_data_ranges([json.loads(line[1]) for line in lines]) if print_data_ranges else None
    problem = json.loads(lines[0][1])
    structure = print_json_structure(problem, data_ranges=data_ranges)
    print_code(structure, print_line_numbers=args.line_numbers, lexer="python")


def remove_type_keys(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: remove_type_keys(v) for k, v in data.items() if k != "__type"}
    elif isinstance(data, list):
        return [remove_type_keys(item) for item in data]
    else:
        return data


def truncate_strings(data, max_length):
    if isinstance(data, dict):
        return {k: truncate_strings(v, max_length) for k, v in data.items()}
    elif isinstance(data, list):
        return [truncate_strings(item, max_length) for item in data]
    elif isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + f"... ({len(data) - max_length} characters truncated)"
        else:
            return data
    else:
        return data


def iterate_over_problems(args, lines):
    problem_number = args.start if args.start else 0  # For the post-loop filtering summary
    filter_included = 0
    try:
        for selection_index, (original_index, line) in enumerate(lines):
            problem_number += 1
            if args.renumber:
                print_header_1(f"Problem {selection_index + 1}")
            else:
                print_header_1(f"Problem {original_index}")
            try:
                problem = json.loads(line)
            except json.JSONDecodeError:
                print_text(f"Problem on line {original_index} is not valid JSON")
                continue
            if args.raw:
                p = problem
                if args.max_str_len:
                    p = truncate_strings(p, args.max_str_len)
                print_code(json.dumps(p, indent=4), print_line_numbers=args.line_numbers, lexer="json")
            else:
                print_problem(problem, parts=args.parts, print_line_numbers=args.line_numbers)
            if args.manual_filter:
                include = input(f"Include this problem in {args.filter_output}? (y/N/q) ")
                if include.lower() == "q":
                    raise KeyboardInterrupt()
                if include.lower() == "y":
                    filter_included += 1
                    with open(args.filter_output, "a") as f:
                        f.write(json.dumps(problem) + "\n")
    except KeyboardInterrupt:
        if args.manual_filter:
            print_text("")
            print_header_1("Manual Filtering Statistics")
            print_text(f"Manually selected {filter_included} problems from {args.file}.")
            if not args.randomize:
                print_code(
                    f"From lines: {args.start} to {problem_number - 1}. Next time use `--start {problem_number - 1}` to resume.",
                    lexer="markdown",
                )
            print_code(
                f"Output to file: {args.filter_output}, use `pprint_problems {args.filter_output}` to view.",
                lexer="markdown",
            )
