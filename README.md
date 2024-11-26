# pprint_problems

Used to print entries from jsonl files, developed with LLM evals in mind.

## Installation

```pipx install pprint_problems```

## Development

This is still a work in progress. If you have any suggestions or improvements, please feel free to open an issue or a pull request, or contact the author directly.

## Usage

Here are some recommended ways to use this script:

```
See this list of commands and more documentation:
    pprint_problems --help

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

12. Print the structure, along with stats about the ranges of values:
    pprint_problems mydata.jsonl --structure --ranges
```

### Structure

Here's an example of how to use this program to print out the structure of a dataset:

```bash
pprint_problems mydata.jsonl --structure --ranges
```

Which will yield something like the following:

```bash
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                           JSON Structure (problem 0), with Data Ranges from 50 Samples                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{
    "doc_id": int (0 to 49, avg: 24.5)
    "doc": dict (2 items)
    {
        "question": str (322 characters) (50 distinct values, length: 200 to 1845)
        "scoring_guide": dict (14 items)
        {
            "premises": list[list[str]] (2 items) (Lengths: 2 to 2)
            "full_prose": str (322 characters) (50 distinct values, length: 200 to 1845)
            "question_conclusion": list[str] (2 items) (Lengths: 2 to 2)
            "etr_conclusion": list[str] (2 items) (Lengths: 2 to 2)
            "etr_conclusion_is_categorical": bool (74% False, 26% True)
            "question_conclusion_is_etr_conclusion": bool (100% True)
            "classically_valid_conclusion": bool (80% False, 20% True)
            "vocab_size": int (2 to 6, avg: 3.74)
            "max_disjuncts": int (1 to 12, avg: 3.6)
            "num_variables": int (2 to 11, avg: 6.36)
            "num_disjuncts": int (2 to 6, avg: 4.06)
            "num_premises": int (100% 2)
            "etr_answer": str (3 characters) (74% NO, 26% YES)
            "logically_correct_answer": str (2 characters) (80% NO, 20% YES)
        }
    }
    "target": str (1197 characters) (50 distinct values, length: 844 to 7552)
    "arguments": dict (1 items)
    {
        "gen_args_0": dict (2 items)
        {
            "arg_0": list[str] (1 items) (Lengths: 1 to 1)
            "arg_1": dict (4 items)
            {
                "until": list[str] (1 items) (Lengths: 1 to 1)
                "do_sample": bool (100% False)
                "temperature": float (100% 0.2)
                "max_gen_toks": int (100% 2000)
            }
        }
    }
    "resps": list[list[str]] (1 items) (Lengths: 1 to 1)
    "filtered_resps": list[str] (1 items) (Lengths: 1 to 1)
    "doc_hash": str (64 characters) (50 distinct values, length: 64 to 64)
    "prompt_hash": str (64 characters) (50 distinct values, length: 64 to 64)
    "target_hash": str (64 characters) (50 distinct values, length: 64 to 64)
    "correct": float (70% 0.0, 30% 1.0)
    "len_response": int (14% 2, 86% 3)
}
```

## License

This project is licensed under the terms of the MIT license.