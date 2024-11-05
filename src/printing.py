try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.syntax import Syntax

    USE_RICH = True
except ImportError:
    USE_RICH = False


WIDTH = 100
if USE_RICH:
    console = Console(force_terminal=True)

MAX_PRINT_LEN = None


def set_max_print_len(length: int | None) -> None:
    global MAX_PRINT_LEN 
    MAX_PRINT_LEN = length



def print_header_1(text: str) -> None:
    if USE_RICH:
        console.print(Markdown(f"# {text}"))
    else:
        space = (WIDTH - len(text)) // 2
        print("*" * WIDTH)
        print(" " * space + text)
        print("*" * WIDTH)


def print_header_2(text: str) -> None:
    if USE_RICH:
        console.print(Markdown(f"## {text}"))
    else:
        space = (WIDTH - len(text)) // 2
        underline_start = "\033[4m"
        underline_end = "\033[0m"
        print("\n" + " " * space + underline_start + text + underline_end)


def print_header_3(text: str) -> None:
    if USE_RICH:
        console.print(Markdown(f"### {text}"))
    else:
        print(f"\n**** {text} ****\n")


def print_text(text: str) -> None:
    if MAX_PRINT_LEN is not None and len(text) > MAX_PRINT_LEN:
        text = text[:MAX_PRINT_LEN] + f"... ({len(text) - MAX_PRINT_LEN} characters truncated)"
    if USE_RICH:
        console.print(Markdown(text))
    else:
        print(text)


def print_code(code: str, print_line_numbers: bool = False, lexer: str = "python") -> None:
    if MAX_PRINT_LEN is not None and len(code) > MAX_PRINT_LEN:
        code = code[:MAX_PRINT_LEN] + f"... ({len(code) - MAX_PRINT_LEN} characters truncated)"
    if USE_RICH:
        console.print(Syntax(code, lexer, theme="monokai", line_numbers=print_line_numbers, word_wrap=True))
    else:
        for i, l in enumerate(code.split("\n")):
            if print_line_numbers:
                print(f"{i + 1:3}:\t{l}")
            else:
                print(l)


def print_file_output(args):
    if USE_RICH:
        if args.file_output.lower().endswith(".html"):
            console.save_html(args.file_output)
        else:
            console.save_text(args.file_output)
    else:
        raise NotImplementedError(
            "File output is only supported with the rich library. Use `> output.txt` instead."
        )


def configure_console(args):
    global WIDTH
    if USE_RICH:
        global console
        if args.width and args.width != WIDTH:
            console = Console(force_terminal=True, width=args.width, record=True)
        else:
            console = Console(force_terminal=True, record=True)
    WIDTH = args.width
