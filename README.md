# pprint_problems

Alternative to the `jq` command that's a bit optimized for LLM eval datasets in jsonl format. 

## Installation

```pip install pprint_problems```

## Development

This is still a work in progress. If you have any suggestions or improvements, please feel free to open an issue or a pull request, or contact the author directly.

## Usage

Here are some recommended ways to use this script:

```
1. Search for particular problems:
    pprint_problems problems.jsonl -r --search "keyword" -b

2. Load a local file:
    pprint_problems test_problems.jsonl --randomize -n 1 --parts code tests

3. Load a local file with "cat":
    cat problems.jsonl | grep "search_term" | pprint_problems -n 1 -p code

4. Load and randomize problems:
    pprint_problems -r -n 1 problems.jsonl

5. Use some arguments to only load a subset:
    pprint_problems my_problems.jsonl --n 3 --width 100 --line-numbers --randomize

6. Print out the structure:
    pprint_problems --structure test_data.jsonl

7. Print out the raw JSON:
    pprint_problems --n 1 --raw problems.jsonl

8. Manually filter problems with y/n on the keyboard:
    pprint_problems problems.jsonl --manual-filter -p code broken_diff

9. Use the most recently modified file in a directory:
    pprint_problems --dir_most_recent my_jsonl_files/ --structure

10. Graph the distribution of a particular key:
    pprint_problems mydata.jsonl --graph --parts vocab_size

11. Print stats, similarly to graphing:
    pprint_problems mydata.jsonl --stats --parts vocab_size
```

## License

This project is licensed under the terms of the MIT license.