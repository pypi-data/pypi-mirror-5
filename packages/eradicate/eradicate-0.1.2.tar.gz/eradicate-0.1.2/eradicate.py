# Copyright (C) 2012-2013 Steven Myint
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Removes commented-out Python code."""

from __future__ import print_function

from io import StringIO
import os
import re
import tokenize

__version__ = '0.1.2'


try:
    unicode
except NameError:
    unicode = str


def comment_contains_code(line):
    """Return True comment contains code."""
    line = line.lstrip()
    if not line.startswith('#'):
        return False

    line = line.lstrip(' \t\v\n#').strip()

    # Ignore non-comment related hashes. For example, "# Issue #999".
    if re.search('#[0-9]', line):
        return False

    # Check that this is possibly code.
    for symbol in list('()[]{}:=') + ['print', 'return', 'break', 'continue',
                                      'import']:
        if symbol in line:
            break
    else:
        return False

    # Handle multi-line cases manually.
    for ending in ')]}':
        if line.endswith(ending + ':'):
            return True

    for symbol in ['else', 'try', 'finally']:
        if re.match(r'^\s*' + symbol + r'\s*:\s*$', line):
            return True

    for remove_beginning in ['print', 'return']:
        line = re.sub('^' + remove_beginning + r'\b\s*', '', line)

    try:
        compile(line, '<string>', 'exec')
        return True
    except (SyntaxError, TypeError, UnicodeDecodeError):
        return False


def commented_out_code_line_numbers(source):
    """Yield line numbers of commented-out code."""
    sio = StringIO(source)
    try:
        for token in tokenize.generate_tokens(sio.readline):
            token_type = token[0]
            start_row = token[2][0]
            line = token[4]

            if (token_type == tokenize.COMMENT and
                    line.lstrip().startswith('#') and
                    comment_contains_code(line)):
                yield start_row
    except (tokenize.TokenError, IndentationError):
        pass


def filter_commented_out_code(source):
    """Yield code with commented out code removed."""
    marked_lines = list(commented_out_code_line_numbers(source))
    sio = StringIO(source)
    previous_line = ''
    for line_number, line in enumerate(sio.readlines(), start=1):
        if (line_number not in marked_lines or
                previous_line.rstrip().endswith('\\')):
            yield line
        previous_line = line


def fix_file(filename, args, standard_out):
    """Run filter_commented_out_code() on file."""
    encoding = detect_encoding(filename)
    with open_with_encoding(filename, encoding=encoding) as input_file:
        source = input_file.read()

    filtered_source = unicode().join(filter_commented_out_code(source))

    if source != filtered_source:
        if args.in_place:
            with open_with_encoding(filename, mode='w',
                                    encoding=encoding) as output_file:
                output_file.write(filtered_source)
        else:
            import difflib
            diff = difflib.unified_diff(
                source.splitlines(),
                filtered_source.splitlines(),
                'before/' + filename,
                'after/' + filename,
                lineterm='')
            standard_out.write(unicode('\n').join(list(diff) + ['']))


def open_with_encoding(filename, encoding, mode='r'):
    """Return opened file with a specific encoding."""
    import io
    return io.open(filename, mode=mode, encoding=encoding,
                   newline='')  # Preserve line endings


def detect_encoding(filename):
    """Return file encoding."""
    try:
        with open(filename, 'rb') as input_file:
            from lib2to3.pgen2 import tokenize as lib2to3_tokenize
            encoding = lib2to3_tokenize.detect_encoding(input_file.readline)[0]

            # Check for correctness of encoding.
            with open_with_encoding(filename, encoding) as input_file:
                input_file.read()

        return encoding
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return 'latin-1'


def main(argv, standard_out, standard_error):
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, prog='eradicate')
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='make changes to files instead of printing diffs')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='drill down directories recursively')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+', help='files to format')

    args = parser.parse_args(argv[1:])

    filenames = list(set(args.files))
    while filenames:
        name = filenames.pop(0)
        if args.recursive and os.path.isdir(name):
            for root, directories, children in os.walk(name):
                filenames += [os.path.join(root, f) for f in children
                              if f.endswith('.py') and
                              not f.startswith('.')]
                directories[:] = [d for d in directories
                                  if not d.startswith('.')]
        else:
            try:
                fix_file(name, args=args, standard_out=standard_out)
            except IOError as exception:
                print(unicode(exception), file=standard_error)
