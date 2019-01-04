
import argparse
import sys
import re


def output(line):
    print(line)


def grep(lines, params):
    def add_context_lines(line_number, before=True):
        if before:
            for i in range(1, line_number + 1):
                if line_index - i >= 0 and line_index - i + 1 not in result_output:
                    result_output.update({line_index - i + 1: {'line': lines[line_index - i], 'isFounded': False}})
        else:
            for i in range(1, line_number + 1):
                if line_index + i < len(lines) and line_index + i + 1 not in result_output:
                    result_output.update({line_index + i + 1: {'line': lines[line_index + i], 'isFounded': False}})

    result_output = {}
    regexp = create_regexp(params)
    for line in lines:
        line = line.rstrip()

        if (re.search(regexp, line) and not params.invert) or (not re.search(regexp, line) and params.invert):
            line_index = lines.index(line)
            result_output.update({line_index + 1: {'line': line, 'isFounded': True}})

            if params.context:
                add_context_lines(params.context)
                add_context_lines(params.context, False)

            if params.before_context:
                add_context_lines(params.before_context)

            if params.after_context:
                add_context_lines(params.after_context, False)

    for line in format_output(params, result_output):
        output(line)


def format_output(params, lines):
    def sort_dict(lines):
        sorted_dict = {}
        for key in sorted(lines.keys()):
            sorted_dict.update({key: lines[key]})
        return sorted_dict

    lines = sort_dict(lines)
    if params.count:
        if lines:
            return [str(len(lines))]
        else:
            return [str(0)]

    if params.line_number:
        return [f"{key}:{value['line']}" if value['isFounded'] else f"{key}-{value['line']}" for key, value in lines.items()]

    else:
        return [value['line'] for value in lines.values()]


def create_regexp(params):
    regexp = re.escape(params.pattern)
    regexp = re.sub(r'\\\?', '.', regexp)
    regexp = re.sub(r'\\\*', '.*', regexp)

    if params.ignore_case:
        return re.compile(regexp, re.IGNORECASE)
    else:
        return re.compile(regexp)


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
