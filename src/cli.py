#!/usr/bin/env python3

import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Pretty print problems from jsonl files"
    )
    parser.add_argument(
        "file", 
        nargs="?", 
        type=argparse.FileType('r'),
        help="Input file (optional, defaults to stdin)",
        default=None
    )
    
    args = parser.parse_args()
    print("Hello from pprint_problems!")
    
if __name__ == "__main__":
    main()
