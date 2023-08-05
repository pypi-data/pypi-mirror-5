#!/usr/bin/env python
# pep8.py - Check Python source code formatting, according to PEP 8
# Copyright (C) 2006-2009 Johann C. Rocholl <johann@rocholl.net>
# Copyright (C) 2009-2013 Florent Xicluna <florent.xicluna@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

r"""
Check Python source code formatting, according to PEP 8:
http://www.python.org/dev/peps/pep-0008/

For usage and a list of options, try this:
$ python pep8.py -h

This program and its regression test suite live here:
http://github.com/jcrocholl/pep8

Groups of errors and warnings:
E errors
W warnings
100 indentation
200 whitespace
300 blank lines
400 imports
500 line length
600 deprecation
700 statements
900 syntax error
"""
__version__ = '1.4.6a0'

import os
import sys
import re
import time
import inspect
import keyword
import tokenize
from optparse import OptionParser
from fnmatch import fnmatch
try:
    from configparser import RawConfigParser
    from io import TextIOWrapper
except ImportError:
    from ConfigParser import RawConfigParser

DEFAULT_EXCLUDE = '.svn,CVS,.bzr,.hg,.git,__pycache__'
DEFAULT_IGNORE = 'E226,E24'
if sys.platform == 'win32':
    DEFAULT_CONFIG = os.path.expanduser(r'~\.pep8')
else:
    DEFAULT_CONFIG = os.path.join(os.getenv('XDG_CONFIG_HOME') or
                                  os.path.expanduser('~/.config'), 'pep8')
PROJECT_CONFIG = ('setup.cfg', 'tox.ini', '.pep8')
TESTSUITE_PATH = os.path.join(os.path.dirname(__file__), 'testsuite')
MAX_LINE_LENGTH = 79
REPORT_FORMAT = {
    'default': '%(path)s:%(row)d:%(col)d: %(code)s %(text)s',
    'pylint': '%(path)s:%(row)d: [%(code)s] %(text)s',
}

PyCF_ONLY_AST = 1024
SINGLETONS = frozenset(['False', 'None', 'True'])
KEYWORDS = frozenset(keyword.kwlist + ['print']) - SINGLETONS
UNARY_OPERATORS = frozenset(['>>', '**', '*', '+', '-'])
ARITHMETIC_OP = frozenset(['**', '*', '/', '//', '+', '-'])
WS_OPTIONAL_OPERATORS = ARITHMETIC_OP.union(['^', '&', '|', '<<', '>>', '%'])
WS_NEEDED_OPERATORS = frozenset([
    '**=', '*=', '/=', '//=', '+=', '-=', '!=', '<>', '<', '>',
    '%=', '^=', '&=', '|=', '==', '<=', '>=', '<<=', '>>=', '='])
WHITESPACE = frozenset(' \t')
SKIP_TOKENS = frozenset([tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                         tokenize.INDENT, tokenize.DEDENT])
BENCHMARK_KEYS = ['directories', 'files', 'logical lines', 'physical lines']

INDENT_REGEX = re.compile(r'([ \t]*)')
RAISE_COMMA_REGEX = re.compile(r'raise\s+\w+\s*,')
RERAISE_COMMA_REGEX = re.compile(r'raise\s+\w+\s*,\s*\w+\s*,\s*\w+')
ERRORCODE_REGEX = re.compile(r'\b[A-Z]\d{3}\b')
DOCSTRING_REGEX = re.compile(r'u?r?["\']')
EXTRANEOUS_WHITESPACE_REGEX = re.compile(r'[[({] | []}),;:]')
WHITESPACE_AFTER_COMMA_REGEX = re.compile(r'[,;:]\s*(?:  |\t)')
COMPARE_SINGLETON_REGEX = re.compile(r'([=!]=)\s*(None|False|True)')
COMPARE_TYPE_REGEX = re.compile(r'(?:[=!]=|is(?:\s+not)?)\s*type(?:s.\w+Type'
                                r'|\s*\(\s*([^)]*[^ )])\s*\))')
KEYWORD_REGEX = re.compile(r'(\s*)\b(?:%s)\b(\s*)' % r'|'.join(KEYWORDS))
OPERATOR_REGEX = re.compile(r'(?:[^,\s])(\s*)(?:[-+*/|!<=>%&^]+)(\s*)')
LAMBDA_REGEX = re.compile(r'\blambda\b')
HUNK_REGEX = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@.*$')

# Work around Python < 2.6 behaviour, which does not generate NL after
# a comment which is on a line by itself.
COMMENT_WITH_NL = tokenize.generate_tokens(['#\n'].pop).send(None)[1] == '#\n'


##############################################################################
# Plugins (check functions) for physical lines
##############################################################################


def tabs_or_spaces(physical_line, indent_char):
    r"""
    Never mix tabs and spaces.

    The most popular way of indenting Python is with spaces only.  The
    second-most popular way is with tabs only.  Code indented with a mixture
    of tabs and spaces should be converted to using spaces exclusively.  When
    invoking the Python command line interpreter with the -t option, it issues
    warnings about code that illegally mixes tabs and spaces.  When using -tt
    these warnings become errors.  These options are highly recommended!

    Okay: if a == 0:\n        a = 1\n        b = 1
    E101: if a == 0:\n        a = 1\n\tb = 1
    """
    indent = INDENT_REGEX.match(physical_line).group(1)
    for offset, char in enumerate(indent):
        if char != indent_char:
            return offset, "E101 indentation contains mixed spaces and tabs"


def tabs_obsolete(physical_line):
    r"""
    For new projects, spaces-only are strongly recommended over tabs.  Most
    editors have features that make this easy to do.

    Okay: if True:\n    return
    W191: if True:\n\treturn
    """
    indent = INDENT_REGEX.match(physical_line).group(1)
    if '\t' in indent:
        return indent.index('\t'), "W191 indentation contains tabs"


def trailing_whitespace(physical_line):
    r"""
    JCR: Trailing whitespace is superfluous.
    FBM: Except when it occurs as part of a blank line (i.e. the line is
         nothing but whitespace). According to Python docs[1] a line with only
         whitespace is considered a blank line, and is to be ignored. However,
         matching a blank line to its indentation level avoids mistakenly
         terminating a multi-line statement (e.g. class declaration) when
         pasting code into the standard Python interpreter.

         [1] http://docs.python.org/reference/lexical_analysis.html#blank-lines

    The warning returned varies on whether the line itself is blank, for easier
    filtering for those who want to indent their blank lines.

    Okay: spam(1)\n#
    W291: spam(1) \n#
    W293: class Foo(object):\n    \n    bang = 12
    """
    physical_line = physical_line.rstrip('\n')    # chr(10), newline
    physical_line = physical_line.rstrip('\r')    # chr(13), carriage return
    physical_line = physical_line.rstrip('\x0c')  # chr(12), form feed, ^L
    stripped = physical_line.rstrip(' \t\v')
    if physical_line != stripped:
        if stripped:
            return len(stripped), "W291 trailing whitespace"
        else:
            return 0, "W293 blank line contains whitespace"


def trailing_blank_lines(physical_line, lines, line_number):
    r"""
    JCR: Trailing blank lines are superfluous.

    Okay: spam(1)
    W391: spam(1)\n
    """
    if not physical_line.rstrip() and line_number == len(lines):
        return 0, "W391 blank line at end of file"


def missing_newline(physical_line):
    """
    JCR: The last line should have a newline.

    Reports warning W292.
    """
    if physical_line.rstrip() == physical_line:
        return len(physical_line), "W292 no newline at end of file"


def maximum_line_length(physical_line, max_line_length):
    """
    Limit all lines to a maximum of 79 characters.

    There are still many devices around that are limited to 80 character
    lines; plus, limiting windows to 80 characters makes it possible to have
    several windows side-by-side.  The default wrapping on such devices looks
    ugly.  Therefore, please limit all lines to a maximum of 79 characters.
    For flowing long blocks of text (docstrings or comments), limiting the
    length to 72 characters is recommended.

    Reports error E501.
    """
    line = physical_line.rstrip()
    length = len(line)
    if length > max_line_length and not noqa(line):
        if hasattr(line, 'decode'):   # Python 2
            # The line could contain multi-byte characters
            try:
                length = len(line.decode('utf-8'))
            except UnicodeError:
                pass
        if length > max_line_length:
            return (max_line_length, "E501 line too long "
                    "(%d > %d characters)" % (length, max_line_length))


##############################################################################
# Plugins (check functions) for logical lines
##############################################################################


def blank_lines(logical_line, blank_lines, indent_level, line_number,
                previous_logical, previous_indent_level):
    r"""
    Separate top-level function and class definitions with two blank lines.

    Method definitions inside a class are separated by a single blank line.

    Extra blank lines may be used (sparingly) to separate groups of related
    functions.  Blank lines may be omitted between a bunch of related
    one-liners (e.g. a set of dummy implementations).

    Use blank lines in functions, sparingly, to indicate logical sections.

    Okay: def a():\n    pass\n\n\ndef b():\n    pass
    Okay: def a():\n    pass\n\n\n# Foo\n# Bar\n\ndef b():\n    pass

    E301: class Foo:\n    b = 0\n    def bar():\n        pass
    E302: def a():\n    pass\n\ndef b(n):\n    pass
    E303: def a():\n    pass\n\n\n\ndef b(n):\n    pass
    E303: def a():\n\n\n\n    pass
    E304: @decorator\n\ndef a():\n    pass
    """
    if line_number < 3 and not previous_logical:
        return  # Don't expect blank lines before the first line
    if previous_logical.startswith('@'):
        if blank_lines:
            yield 0, "E304 blank lines found after function decorator"
    elif blank_lines > 2 or (indent_level and blank_lines == 2):
        yield 0, "E303 too many blank lines (%d)" % blank_lines
    elif logical_line.startswith(('def ', 'class ', '@')):
        if indent_level:
            if not (blank_lines or previous_indent_level < indent_level or
                    DOCSTRING_REGEX.match(previous_logical)):
                yield 0, "E301 expected 1 blank line, found 0"
        elif blank_lines != 2:
            yield 0, "E302 expected 2 blank lines, found %d" % blank_lines


def extraneous_whitespace(logical_line):
    """
    Avoid extraneous whitespace in the following situations:

    - Immediately inside parentheses, brackets or braces.

    - Immediately before a comma, semicolon, or colon.

    Okay: spam(ham[1], {eggs: 2})
    E201: spam( ham[1], {eggs: 2})
    E201: spam(ham[ 1], {eggs: 2})
    E201: spam(ham[1], { eggs: 2})
    E202: spam(ham[1], {eggs: 2} )
    E202: spam(ham[1 ], {eggs: 2})
    E202: spam(ham[1], {eggs: 2 })

    E203: if x == 4: print x, y; x, y = y , x
    E203: if x == 4: print x, y ; x, y = y, x
    E203: if x == 4 : print x, y; x, y = y, x
    """
    line = logical_line
    for match in EXTRANEOUS_WHITESPACE_REGEX.finditer(line):
        text = match.group()
        char = text.strip()
        found = match.start()
        if text == char + ' ':
            # assert char in '([{'
            yield found + 1, "E201 whitespace after '%s'" % char
        elif line[found - 1] != ',':
            code = ('E202' if char in '}])' else 'E203')  # if char in ',;:'
            yield found, "%s whitespace before '%s'" % (code, char)


def whitespace_around_keywords(logical_line):
    r"""
    Avoid extraneous whitespace around keywords.

    Okay: True and False
    E271: True and  False
    E272: True  and False
    E273: True and\tFalse
    E274: True\tand False
    """
    for match in KEYWORD_REGEX.finditer(logical_line):
        before, after = match.groups()

        if '\t' in before:
            yield match.start(1), "E274 tab before keyword"
        elif len(before) > 1:
            yield match.start(1), "E272 multiple spaces before keyword"

        if '\t' in after:
            yield match.start(2), "E273 tab after keyword"
        elif len(after) > 1:
            yield match.start(2), "E271 multiple spaces after keyword"


def missing_whitespace(logical_line):
    """
    JCR: Each comma, semicolon or colon should be followed by whitespace.

    Okay: [a, b]
    Okay: (3,)
    Okay: a[1:4]
    Okay: a[:4]
    Okay: a[1:]
    Okay: a[1:4:2]
    E231: ['a','b']
    E231: foo(bar,baz)
    E231: [{'a':'b'}]
    """
    line = logical_line
    for index in range(len(line) - 1):
        char = line[index]
        if char in ',;:' and line[index + 1] not in WHITESPACE:
            before = line[:index]
            if char == ':' and before.count('[') > before.count(']') and \
                    before.rfind('{') < before.rfind('['):
                continue  # Slice syntax, no space required
            if char == ',' and line[index + 1] == ')':
                continue  # Allow tuple with only one element: (3,)
            yield index, "E231 missing whitespace after '%s'" % char


def indentation(logical_line, previous_logical, indent_char,
                indent_level, previous_indent_level):
    r"""
    Use 4 spaces per indentation level.

    For really old code that you don't want to mess up, you can continue to
    use 8-space tabs.

    Okay: a = 1
    Okay: if a == 0:\n    a = 1
    E111:   a = 1

    Okay: for item in items:\n    pass
    E112: for item in items:\npass

    Okay: a = 1\nb = 2
    E113: a = 1\n    b = 2
    """
    if indent_char == ' ' and indent_level % 4:
        yield 0, "E111 indentation is not a multiple of four"
    indent_expect = previous_logical.endswith(':')
    if indent_expect and indent_level <= previous_indent_level:
        yield 0, "E112 expected an indented block"
    if indent_level > previous_indent_level and not indent_expect:
        yield 0, "E113 unexpected indentation"


def continued_indentation(logical_line, tokens, indent_level, noqa, verbose):
    r"""
    Continuation lines should align wrapped elements either vertically using
    Python's implicit line joining inside parentheses, brackets and braces, or
    using a hanging indent.

    When using a hanging indent the following considerations should be applied:

    - there should be no arguments on the first line, and

    - further indentation should be used to clearly distinguish itself as a
      continuation line.

    Okay: a = (\n)
    E123: a = (\n    )

    Okay: a = (\n    42)
    E121: a = (\n   42)
    E122: a = (\n42)
    E123: a = (\n    42\n    )
    E124: a = (24,\n     42\n)
    E125: if (a or\n    b):\n    pass
    E126: a = (\n        42)
    E127: a = (24,\n      42)
    E128: a = (24,\n    42)
    """
    first_row = tokens[0][2][0]
    nrows = 1 + tokens[-1][2][0] - first_row
    if noqa or nrows == 1:
        return

    # indent_next tells us whether the next block is indented; assuming
    # that it is indented by 4 spaces, then we should not allow 4-space
    # indents on the final continuation line; in turn, some other
    # indents are allowed to have an extra 4 spaces.
    indent_next = logical_line.endswith(':')

    row = depth = 0
    # remember how many brackets were opened on each line
    parens = [0] * nrows
    # relative indents of physical lines
    rel_indent = [0] * nrows
    # visual indents
    indent_chances = {}
    last_indent = tokens[0][2]
    indent = [last_indent[1]]
    if verbose >= 3:
        print(">>> " + tokens[0][4].rstrip())

    for token_type, text, start, end, line in tokens:

        newline = row < start[0] - first_row
        if newline:
            row = start[0] - first_row
            newline = (not last_token_multiline and
                       token_type not in (tokenize.NL, tokenize.NEWLINE))

        if newline:
            # this is the beginning of a continuation line.
            last_indent = start
            if verbose >= 3:
                print("... " + line.rstrip())

            # record the initial indent.
            rel_indent[row] = expand_indent(line) - indent_level

            if depth:
                # a bracket expression in a continuation line.
                # find the line that it was opened on
                for open_row in range(row - 1, -1, -1):
                    if parens[open_row]:
                        break
            else:
                # an unbracketed continuation line (ie, backslash)
                open_row = 0
            hang = rel_indent[row] - rel_indent[open_row]
            close_bracket = (token_type == tokenize.OP and text in ']})')
            visual_indent = not close_bracket and indent_chances.get(start[1])

            if close_bracket and indent[depth]:
                # closing bracket for visual indent
                if start[1] != indent[depth]:
                    yield (start, "E124 closing bracket does not match "
                           "visual indentation")
            elif close_bracket and not hang:
                # closing bracket matches indentation of opening bracket's line
                pass
            elif visual_indent is True:
                # visual indent is verified
                if not indent[depth]:
                    indent[depth] = start[1]
            elif visual_indent in (text, str):
                # ignore token lined up with matching one from a previous line
                pass
            elif indent[depth] and start[1] < indent[depth]:
                # visual indent is broken
                yield (start, "E128 continuation line "
                       "under-indented for visual indent")
            elif hang == 4 or (indent_next and rel_indent[row] == 8):
                # hanging indent is verified
                if close_bracket:
                    yield (start, "E123 closing bracket does not match "
                           "indentation of opening bracket's line")
            else:
                # indent is broken
                if hang <= 0:
                    error = "E122", "missing indentation or outdented"
                elif indent[depth]:
                    error = "E127", "over-indented for visual indent"
                elif hang % 4:
                    error = "E121", "indentation is not a multiple of four"
                else:
                    error = "E126", "over-indented for hanging indent"
                yield start, "%s continuation line %s" % error

        # look for visual indenting
        if (parens[row] and token_type not in (tokenize.NL, tokenize.COMMENT)
                and not indent[depth]):
            indent[depth] = start[1]
            indent_chances[start[1]] = True
            if verbose >= 4:
                print("bracket depth %s indent to %s" % (depth, start[1]))
        # deal with implicit string concatenation
        elif (token_type in (tokenize.STRING, tokenize.COMMENT) or
              text in ('u', 'ur', 'b', 'br')):
            indent_chances[start[1]] = str
        # special case for the "if" statement because len("if (") == 4
        elif not indent_chances and not row and not depth and text == 'if':
            indent_chances[end[1] + 1] = True

        # keep track of bracket depth
        if token_type == tokenize.OP:
            if text in '([{':
                depth += 1
                indent.append(0)
                parens[row] += 1
                if verbose >= 4:
                    print("bracket depth %s seen, col %s, visual min = %s" %
                          (depth, start[1], indent[depth]))
            elif text in ')]}' and depth > 0:
                # parent indents should not be more than this one
                prev_indent = indent.pop() or last_indent[1]
                for d in range(depth):
                    if indent[d] > prev_indent:
                        indent[d] = 0
                for ind in list(indent_chances):
                    if ind >= prev_indent:
                        del indent_chances[ind]
                depth -= 1
                if depth:
                    indent_chances[indent[depth]] = True
                for idx in range(row, -1, -1):
                    if parens[idx]:
                        parens[idx] -= 1
                        break
            assert len(indent) == depth + 1
            if start[1] not in indent_chances:
                # allow to line up tokens
                indent_chances[start[1]] = text

        last_token_multiline = (start[0] != end[0])

    if indent_next and rel_indent[-1] == 4:
        yield (last_indent, "E125 continuation line does not distinguish "
               "itself from next logical line")


def whitespace_before_parameters(logical_line, tokens):
    """
    Avoid extraneous whitespace in the following situations:

    - Immediately before the open parenthesis that starts the argument
      list of a function call.

    - Immediately before the open parenthesis that starts an indexing or
      slicing.

    Okay: spam(1)
    E211: spam (1)

    Okay: dict['key'] = list[index]
    E211: dict ['key'] = list[index]
    E211: dict['key'] = list [index]
    """
    prev_type, prev_text, __, prev_end, __ = tokens[0]
    for index in range(1, len(tokens)):
        token_type, text, start, end, __ = tokens[index]
        if (token_type == tokenize.OP and
            text in '([' and
            start != prev_end and
            (prev_type == tokenize.NAME or prev_text in '}])') and
            # Syntax "class A (B):" is allowed, but avoid it
            (index < 2 or tokens[index - 2][1] != 'class') and
                # Allow "return (a.foo for a in range(5))"
                not keyword.iskeyword(prev_text)):
            yield prev_end, "E211 whitespace before '%s'" % text
        prev_type = token_type
        prev_text = text
        prev_end = end


def whitespace_around_operator(logical_line):
    r"""
    Avoid extraneous whitespace in the following situations:

    - More than one space around an assignment (or other) operator to
      align it with another.

    Okay: a = 12 + 3
    E221: a = 4  + 5
    E222: a = 4 +  5
    E223: a = 4\t+ 5
    E224: a = 4 +\t5
    """
    for match in OPERATOR_REGEX.finditer(logical_line):
        before, after = match.groups()

        if '\t' in before:
            yield match.start(1), "E223 tab before operator"
        elif len(before) > 1:
            yield match.start(1), "E221 multiple spaces before operator"

        if '\t' in after:
            yield match.start(2), "E224 tab after operator"
        elif len(after) > 1:
            yield match.start(2), "E222 multiple spaces after operator"


def missing_whitespace_around_operator(logical_line, tokens):
    r"""
    - Always surround these binary operators with a single space on
      either side: assignment (=), augmented assignment (+=, -= etc.),
      comparisons (==, <, >, !=, <>, <=, >=, in, not in, is, is not),
      Booleans (and, or, not).

    - Use spaces around arithmetic operators.

    Okay: i = i + 1
    Okay: submitted += 1
    Okay: x = x * 2 - 1
    Okay: hypot2 = x * x + y * y
    Okay: c = (a + b) * (a - b)
    Okay: foo(bar, key='word', *args, **kwargs)
    Okay: alpha[:-i]

    E225: i=i+1
    E225: submitted +=1
    E225: x = x /2 - 1
    E225: z = x **y
    E226: c = (a+b) * (a-b)
    E226: hypot2 = x*x + y*y
    E227: c = a|b
    E228: msg = fmt%(errno, errmsg)
    """
    parens = 0
    need_space = False
    prev_type = tokenize.OP
    prev_text = prev_end = None
    for token_type, text, start, end, line in tokens:
        if token_type in (tokenize.NL, tokenize.NEWLINE, tokenize.ERRORTOKEN):
            # ERRORTOKEN is triggered by backticks in Python 3
            continue
        if text in ('(', 'lambda'):
            parens += 1
        elif text == ')':
            parens -= 1
        if need_space:
            if start != prev_end:
                # Found a (probably) needed space
                if need_space is not True and not need_space[1]:
                    yield (need_space[0],
                           "E225 missing whitespace around operator")
                need_space = False
            elif text == '>' and prev_text in ('<', '-'):
                # Tolerate the "<>" operator, even if running Python 3
                # Deal with Python 3's annotated return value "->"
                pass
            else:
                if need_space is True or need_space[1]:
                    # A needed trailing space was not found
                    yield prev_end, "E225 missing whitespace around operator"
                else:
                    code, optype = 'E226', 'arithmetic'
                    if prev_text == '%':
                        code, optype = 'E228', 'modulo'
                    elif prev_text not in ARITHMETIC_OP:
                        code, optype = 'E227', 'bitwise or shift'
                    yield (need_space[0], "%s missing whitespace "
                           "around %s operator" % (code, optype))
                need_space = False
        elif token_type == tokenize.OP and prev_end is not None:
            if text == '=' and parens:
                # Allow keyword args or defaults: foo(bar=None).
                pass
            elif text in WS_NEEDED_OPERATORS:
                need_space = True
            elif text in UNARY_OPERATORS:
                # Check if the operator is being used as a binary operator
                # Allow unary operators: -123, -x, +1.
                # Allow argument unpacking: foo(*args, **kwargs).
                if prev_type == tokenize.OP:
                    binary_usage = (prev_text in '}])')
                elif prev_type == tokenize.NAME:
                    binary_usage = (prev_text not in KEYWORDS)
                else:
                    binary_usage = (prev_type not in SKIP_TOKENS)

                if binary_usage:
                    need_space = None
            elif text in WS_OPTIONAL_OPERATORS:
                need_space = None

            if need_space is None:
                # Surrounding space is optional, but ensure that
                # trailing space matches opening space
                need_space = (prev_end, start != prev_end)
            elif need_space and start == prev_end:
                # A needed opening space was not found
                yield prev_end, "E225 missing whitespace around operator"
                need_space = False
        prev_type = token_type
        prev_text = text
        prev_end = end


def whitespace_around_comma(logical_line):
    r"""
    Avoid extraneous whitespace in the following situations:

    - More than one space around an assignment (or other) operator to
      align it with another.

    Note: these checks are disabled by default

    Okay: a = (1, 2)
    E241: a = (1,  2)
    E242: a = (1,\t2)
    """
    line = logical_line
    for m in WHITESPACE_AFTER_COMMA_REGEX.finditer(line):
        found = m.start() + 1
        if '\t' in m.group():
            yield found, "E242 tab after '%s'" % m.group()[0]
        else:
            yield found, "E241 multiple spaces after '%s'" % m.group()[0]


def whitespace_around_named_parameter_equals(logical_line, tokens):
    """
    Don't use spaces around the '=' sign when used to indicate a
    keyword argument or a default parameter value.

    Okay: def complex(real, imag=0.0):
    Okay: return magic(r=real, i=imag)
    Okay: boolean(a == b)
    Okay: boolean(a != b)
    Okay: boolean(a <= b)
    Okay: boolean(a >= b)

    E251: def complex(real, imag = 0.0):
    E251: return magic(r = real, i = imag)
    """
    parens = 0
    no_space = False
    prev_end = None
    message = "E251 unexpected spaces around keyword / parameter equals"
    for token_type, text, start, end, line in tokens:
        if no_space:
            no_space = False
            if start != prev_end:
                yield (prev_end, message)
        elif token_type == tokenize.OP:
            if text == '(':
                parens += 1
            elif text == ')':
                parens -= 1
            elif parens and text == '=':
                no_space = True
                if start != prev_end:
                    yield (prev_end, message)
        prev_end = end


def whitespace_before_inline_comment(logical_line, tokens):
    """
    Separate inline comments by at least two spaces.

    An inline comment is a comment on the same line as a statement.  Inline
    comments should be separated by at least two spaces from the statement.
    They should start with a # and a single space.

    Okay: x = x + 1  # Increment x
    Okay: x = x + 1    # Increment x
    E261: x = x + 1 # Increment x
    E262: x = x + 1  #Increment x
    E262: x = x + 1  #  Increment x
    """
    prev_end = (0, 0)
    for token_type, text, start, end, line in tokens:
        if token_type == tokenize.COMMENT:
            if not line[:start[1]].strip():
                continue
            if prev_end[0] == start[0] and start[1] < prev_end[1] + 2:
                yield (prev_end,
                       "E261 at least two spaces before inline comment")
            symbol, sp, comment = text.partition(' ')
            if symbol not in ('#', '#:') or comment[:1].isspace():
                yield start, "E262 inline comment should start with '# '"
        elif token_type != tokenize.NL:
            prev_end = end


def imports_on_separate_lines(logical_line):
    r"""
    Imports should usually be on separate lines.

    Okay: import os\nimport sys
    E401: import sys, os

    Okay: from subprocess import Popen, PIPE
    Okay: from myclas import MyClass
    Okay: from foo.bar.yourclass import YourClass
    Okay: import myclass
    Okay: import foo.bar.yourclass
    """
    line = logical_line
    if line.startswith('import '):
        found = line.find(',')
        if -1 < found and ';' not in line[:found]:
            yield found, "E401 multiple imports on one line"


def compound_statements(logical_line):
    r"""
    Compound statements (multiple statements on the same line) are
    generally discouraged.

    While sometimes it's okay to put an if/for/while with a small body
    on the same line, never do this for multi-clause statements. Also
    avoid folding such long lines!

    Okay: if foo == 'blah':\n    do_blah_thing()
    Okay: do_one()
    Okay: do_two()
    Okay: do_three()

    E701: if foo == 'blah': do_blah_thing()
    E701: for x in lst: total += x
    E701: while t < 10: t = delay()
    E701: if foo == 'blah': do_blah_thing()
    E701: else: do_non_blah_thing()
    E701: try: something()
    E701: finally: cleanup()
    E701: if foo == 'blah': one(); two(); three()

    E702: do_one(); do_two(); do_three()
    E703: do_four();  # useless semicolon
    """
    line = logical_line
    last_char = len(line) - 1
    found = line.find(':')
    while -1 < found < last_char:
        before = line[:found]
        if (before.count('{') <= before.count('}') and  # {'a': 1} (dict)
            before.count('[') <= before.count(']') and  # [1:2] (slice)
            before.count('(') <= before.count(')') and  # (Python 3 annotation)
                not LAMBDA_REGEX.search(before)):       # lambda x: x
            yield found, "E701 multiple statements on one line (colon)"
        found = line.find(':', found + 1)
    found = line.find(';')
    while -1 < found:
        if found < last_char:
            yield found, "E702 multiple statements on one line (semicolon)"
        else:
            yield found, "E703 statement ends with a semicolon"
        found = line.find(';', found + 1)


def explicit_line_join(logical_line, tokens):
    r"""
    Avoid explicit line join between brackets.

    The preferred way of wrapping long lines is by using Python's implied line
    continuation inside parentheses, brackets and braces.  Long lines can be
    broken over multiple lines by wrapping expressions in parentheses.  These
    should be used in preference to using a backslash for line continuation.

    E502: aaa = [123, \\n       123]
    E502: aaa = ("bbb " \\n       "ccc")

    Okay: aaa = [123,\n       123]
    Okay: aaa = ("bbb "\n       "ccc")
    Okay: aaa = "bbb " \\n    "ccc"
    """
    prev_start = prev_end = parens = 0
    for token_type, text, start, end, line in tokens:
        if start[0] != prev_start and parens and backslash:
            yield backslash, "E502 the backslash is redundant between brackets"
        if end[0] != prev_end:
            if line.rstrip('\r\n').endswith('\\'):
                backslash = (end[0], len(line.splitlines()[-1]) - 1)
            else:
                backslash = None
            prev_start = prev_end = end[0]
        else:
            prev_start = start[0]
        if token_type == tokenize.OP:
            if text in '([{':
                parens += 1
            elif text in ')]}':
                parens -= 1


def comparison_to_singleton(logical_line, noqa):
    """
    Comparisons to singletons like None should always be done
    with "is" or "is not", never the equality operators.

    Okay: if arg is not None:
    E711: if arg != None:
    E712: if arg == True:

    Also, beware of writing if x when you really mean if x is not None --
    e.g. when testing whether a variable or argument that defaults to None was
    set to some other value.  The other value might have a type (such as a
    container) that could be false in a boolean context!
    """
    match = not noqa and COMPARE_SINGLETON_REGEX.search(logical_line)
    if match:
        same = (match.group(1) == '==')
        singleton = match.group(2)
        msg = "'if cond is %s:'" % (('' if same else 'not ') + singleton)
        if singleton in ('None',):
            code = 'E711'
        else:
            code = 'E712'
            nonzero = ((singleton == 'True' and same) or
                       (singleton == 'False' and not same))
            msg += " or 'if %scond:'" % ('' if nonzero else 'not ')
        yield match.start(1), ("%s comparison to %s should be %s" %
                               (code, singleton, msg))


def comparison_type(logical_line):
    """
    Object type comparisons should always use isinstance() instead of
    comparing types directly.

    Okay: if isinstance(obj, int):
    E721: if type(obj) is type(1):

    When checking if an object is a string, keep in mind that it might be a
    unicode string too! In Python 2.3, str and unicode have a common base
    class, basestring, so you can do:

    Okay: if isinstance(obj, basestring):
    Okay: if type(a1) is type(b1):
    """
    match = COMPARE_TYPE_REGEX.search(logical_line)
    if match:
        inst = match.group(1)
        if inst and isidentifier(inst) and inst not in SINGLETONS:
            return  # Allow comparison for types which are not obvious
        yield match.start(), "E721 do not compare types, use 'isinstance()'"


def python_3000_has_key(logical_line):
    r"""
    The {}.has_key() method is removed in the Python 3.
    Use the 'in' operation instead.

    Okay: if "alph" in d:\n    print d["alph"]
    W601: assert d.has_key('alph')
    """
    pos = logical_line.find('.has_key(')
    if pos > -1:
        yield pos, "W601 .has_key() is deprecated, use 'in'"


def python_3000_raise_comma(logical_line):
    """
    When raising an exception, use "raise ValueError('message')"
    instead of the older form "raise ValueError, 'message'".

    The paren-using form is preferred because when the exception arguments
    are long or include string formatting, you don't need to use line
    continuation characters thanks to the containing parentheses.  The older
    form is removed in Python 3.

    Okay: raise DummyError("Message")
    W602: raise DummyError, "Message"
    """
    match = RAISE_COMMA_REGEX.match(logical_line)
    if match and not RERAISE_COMMA_REGEX.match(logical_line):
        yield match.end() - 1, "W602 deprecated form of raising exception"


def python_3000_not_equal(logical_line):
    """
    != can also be written <>, but this is an obsolete usage kept for
    backwards compatibility only. New code should always use !=.
    The older syntax is removed in Python 3.

    Okay: if a != 'no':
    W603: if a <> 'no':
    """
    pos = logical_line.find('<>')
    if pos > -1:
        yield pos, "W603 '<>' is deprecated, use '!='"


def python_3000_backticks(logical_line):
    """
    Backticks are removed in Python 3.
    Use repr() instead.

    Okay: val = repr(1 + 2)
    W604: val = `1 + 2`
    """
    pos = logical_line.find('`')
    if pos > -1:
        yield pos, "W604 backticks are deprecated, use 'repr()'"


##############################################################################
# Helper functions
##############################################################################


if '' == ''.encode():
    # Python 2: implicit encoding.
    def readlines(filename):
        f = open(filename)
        try:
            return f.readlines()
        finally:
            f.close()
    isidentifier = re.compile(r'[a-zA-Z_]\w*').match
    stdin_get_value = sys.stdin.read
else:
    # Python 3
    def readlines(filename):
        f = open(filename, 'rb')
        try:
            coding, lines = tokenize.detect_encoding(f.readline)
            f = TextIOWrapper(f, coding, line_buffering=True)
            return [l.decode(coding) for l in lines] + f.readlines()
        except (LookupError, SyntaxError, UnicodeError):
            f.close()
            # Fall back if files are improperly declared
            f = open(filename, encoding='latin-1')
            return f.readlines()
        finally:
            f.close()
    isidentifier = str.isidentifier

    def stdin_get_value():
        return TextIOWrapper(sys.stdin.buffer, errors='ignore').read()
readlines.__doc__ = "    Read the source code."
noqa = re.compile(r'# no(?:qa|pep8)\b', re.I).search


def expand_indent(line):
    r"""
    Return the amount of indentation.
    Tabs are expanded to the next multiple of 8.

    >>> expand_indent('    ')
    4
    >>> expand_indent('\t')
    8
    >>> expand_indent('    \t')
    8
    >>> expand_indent('       \t')
    8
    >>> expand_indent('        \t')
    16
    """
    if '\t' not in line:
        return len(line) - len(line.lstrip())
    result = 0
    for char in line:
        if char == '\t':
            result = result // 8 * 8 + 8
        elif char == ' ':
            result += 1
        else:
            break
    return result


def mute_string(text):
    """
    Replace contents with 'xxx' to prevent syntax matching.

    >>> mute_string('"abc"')
    '"xxx"'
    >>> mute_string("'''abc'''")
    "'''xxx'''"
    >>> mute_string("r'abc'")
    "r'xxx'"
    """
    # String modifiers (e.g. u or r)
    start = text.index(text[-1]) + 1
    end = len(text) - 1
    # Triple quotes
    if text[-3:] in ('"""', "'''"):
        start += 2
        end -= 2
    return text[:start] + 'x' * (end - start) + text[end:]


def parse_udiff(diff, patterns=None, parent='.'):
    """Return a dictionary of matching lines."""
    # For each file of the diff, the entry key is the filename,
    # and the value is a set of row numbers to consider.
    rv = {}
    path = nrows = None
    for line in diff.splitlines():
        if nrows:
            if line[:1] != '-':
                nrows -= 1
            continue
        if line[:3] == '@@ ':
            hunk_match = HUNK_REGEX.match(line)
            row, nrows = [int(g or '1') for g in hunk_match.groups()]
            rv[path].update(range(row, row + nrows))
        elif line[:3] == '+++':
            path = line[4:].split('\t', 1)[0]
            if path[:2] == 'b/':
                path = path[2:]
            rv[path] = set()
    return dict([(os.path.join(parent, path), rows)
                 for (path, rows) in rv.items()
                 if rows and filename_match(path, patterns)])


def filename_match(filename, patterns, default=True):
    """
    Check if patterns contains a pattern that matches filename.
    If patterns is unspecified, this always returns True.
    """
    if not patterns:
        return default
    return any(fnmatch(filename, pattern) for pattern in patterns)


##############################################################################
# Framework to run all checks
##############################################################################


_checks = {'physical_line': {}, 'logical_line': {}, 'tree': {}}


def register_check(check, codes=None):
    """
    Register a new check object.
    """
    def _add_check(check, kind, codes, args):
        if check in _checks[kind]:
            _checks[kind][check][0].extend(codes or [])
        else:
            _checks[kind][check] = (codes or [''], args)
    if inspect.isfunction(check):
        args = inspect.getargspec(check)[0]
        if args and args[0] in ('physical_line', 'logical_line'):
            if codes is None:
                codes = ERRORCODE_REGEX.findall(check.__doc__ or '')
            _add_check(check, args[0], codes, args)
    elif inspect.isclass(check):
        if inspect.getargspec(check.__init__)[0][:2] == ['self', 'tree']:
            _add_check(check, 'tree', codes, None)


def init_checks_registry():
    """
    Register all globally visible functions where the first argument name
    is 'physical_line' or 'logical_line'.
    """
    mod = inspect.getmodule(register_check)
    for (name, function) in inspect.getmembers(mod, inspect.isfunction):
        register_check(function)
init_checks_registry()


class Checker(object):
    """
    Load a Python source file, tokenize it, check coding style.
    """

    def __init__(self, filename=None, lines=None,
                 options=None, report=None, **kwargs):
        if options is None:
            options = StyleGuide(kwargs).options
        else:
            assert not kwargs
        self._io_error = None
        self._physical_checks = options.physical_checks
        self._logical_checks = options.logical_checks
        self._ast_checks = options.ast_checks
        self.max_line_length = options.max_line_length
        self.verbose = options.verbose
        self.filename = filename
        if filename is None:
            self.filename = 'stdin'
            self.lines = lines or []
        elif filename == '-':
            self.filename = 'stdin'
            self.lines = stdin_get_value().splitlines(True)
        elif lines is None:
            try:
                self.lines = readlines(filename)
            except IOError:
                exc_type, exc = sys.exc_info()[:2]
                self._io_error = '%s: %s' % (exc_type.__name__, exc)
                self.lines = []
        else:
            self.lines = lines
        if self.lines:
            ord0 = ord(self.lines[0][0])
            if ord0 in (0xef, 0xfeff):  # Strip the UTF-8 BOM
                if ord0 == 0xfeff:
                    self.lines[0] = self.lines[0][1:]
                elif self.lines[0][:3] == '\xef\xbb\xbf':
                    self.lines[0] = self.lines[0][3:]
        self.report = report or options.report
        self.report_error = self.report.error

    def report_invalid_syntax(self):
        exc_type, exc = sys.exc_info()[:2]
        if len(exc.args) > 1:
            offset = exc.args[1]
            if len(offset) > 2:
                offset = offset[1:3]
        else:
            offset = (1, 0)
        self.report_error(offset[0], offset[1] or 0,
                          'E901 %s: %s' % (exc_type.__name__, exc.args[0]),
                          self.report_invalid_syntax)
    report_invalid_syntax.__doc__ = "    Check if the syntax is valid."

    def readline(self):
        """
        Get the next line from the input buffer.
        """
        self.line_number += 1
        if self.line_number > len(self.lines):
            return ''
        return self.lines[self.line_number - 1]

    def readline_check_physical(self):
        """
        Check and return the next physical line. This method can be
        used to feed tokenize.generate_tokens.
        """
        line = self.readline()
        if line:
            self.check_physical(line)
        return line

    def run_check(self, check, argument_names):
        """
        Run a check plugin.
        """
        arguments = []
        for name in argument_names:
            arguments.append(getattr(self, name))
        return check(*arguments)

    def check_physical(self, line):
        """
        Run all physical checks on a raw input line.
        """
        self.physical_line = line
        if self.indent_char is None and line[:1] in WHITESPACE:
            self.indent_char = line[0]
        for name, check, argument_names in self._physical_checks:
            result = self.run_check(check, argument_names)
            if result is not None:
                offset, text = result
                self.report_error(self.line_number, offset, text, check)

    def build_tokens_line(self):
        """
        Build a logical line from tokens.
        """
        self.mapping = []
        logical = []
        comments = []
        length = 0
        previous = None
        for token in self.tokens:
            token_type, text = token[0:2]
            if token_type == tokenize.COMMENT:
                comments.append(text)
                continue
            if token_type in SKIP_TOKENS:
                continue
            if token_type == tokenize.STRING:
                text = mute_string(text)
            if previous:
                end_row, end = previous[3]
                start_row, start = token[2]
                if end_row != start_row:    # different row
                    prev_text = self.lines[end_row - 1][end - 1]
                    if prev_text == ',' or (prev_text not in '{[('
                                            and text not in '}])'):
                        logical.append(' ')
                        length += 1
                elif end != start:  # different column
                    fill = self.lines[end_row - 1][end:start]
                    logical.append(fill)
                    length += len(fill)
            self.mapping.append((length, token))
            logical.append(text)
            length += len(text)
            previous = token
        self.logical_line = ''.join(logical)
        self.noqa = comments and noqa(''.join(comments))
        # With Python 2, if the line ends with '\r\r\n' the assertion fails
        # assert self.logical_line.strip() == self.logical_line

    def check_logical(self):
        """
        Build a line from tokens and run all logical checks on it.
        """
        self.build_tokens_line()
        self.report.increment_logical_line()
        first_line = self.lines[self.mapping[0][1][2][0] - 1]
        indent = first_line[:self.mapping[0][1][2][1]]
        self.previous_indent_level = self.indent_level
        self.indent_level = expand_indent(indent)
        if self.verbose >= 2:
            print(self.logical_line[:80].rstrip())
        for name, check, argument_names in self._logical_checks:
            if self.verbose >= 4:
                print('   ' + name)
            for result in self.run_check(check, argument_names):
                offset, text = result
                if isinstance(offset, tuple):
                    orig_number, orig_offset = offset
                else:
                    for token_offset, token in self.mapping:
                        if offset >= token_offset:
                            orig_number = token[2][0]
                            orig_offset = (token[2][1] + offset - token_offset)
                self.report_error(orig_number, orig_offset, text, check)
        self.previous_logical = self.logical_line

    def check_ast(self):
        try:
            tree = compile(''.join(self.lines), '', 'exec', PyCF_ONLY_AST)
        except (SyntaxError, TypeError):
            return self.report_invalid_syntax()
        for name, cls, _ in self._ast_checks:
            checker = cls(tree, self.filename)
            for lineno, offset, text, check in checker.run():
                if not noqa(self.lines[lineno - 1]):
                    self.report_error(lineno, offset, text, check)

    def generate_tokens(self):
        if self._io_error:
            self.report_error(1, 0, 'E902 %s' % self._io_error, readlines)
        tokengen = tokenize.generate_tokens(self.readline_check_physical)
        try:
            for token in tokengen:
                yield token
        except (SyntaxError, tokenize.TokenError):
            self.report_invalid_syntax()

    def check_all(self, expected=None, line_offset=0):
        """
        Run all checks on the input file.
        """
        self.report.init_file(self.filename, self.lines, expected, line_offset)
        if self._ast_checks:
            self.check_ast()
        self.line_number = 0
        self.indent_char = None
        self.indent_level = 0
        self.previous_logical = ''
        self.tokens = []
        self.blank_lines = blank_lines_before_comment = 0
        parens = 0
        for token in self.generate_tokens():
            self.tokens.append(token)
            token_type, text = token[0:2]
            if self.verbose >= 3:
                if token[2][0] == token[3][0]:
                    pos = '[%s:%s]' % (token[2][1] or '', token[3][1])
                else:
                    pos = 'l.%s' % token[3][0]
                print('l.%s\t%s\t%s\t%r' %
                      (token[2][0], pos, tokenize.tok_name[token[0]], text))
            if token_type == tokenize.OP:
                if text in '([{':
                    parens += 1
                elif text in '}])':
                    parens -= 1
            elif not parens:
                if token_type == tokenize.NEWLINE:
                    if self.blank_lines < blank_lines_before_comment:
                        self.blank_lines = blank_lines_before_comment
                    self.check_logical()
                    self.tokens = []
                    self.blank_lines = blank_lines_before_comment = 0
                elif token_type == tokenize.NL:
                    if len(self.tokens) == 1:
                        # The physical line contains only this token.
                        self.blank_lines += 1
                    self.tokens = []
                elif token_type == tokenize.COMMENT and len(self.tokens) == 1:
                    if blank_lines_before_comment < self.blank_lines:
                        blank_lines_before_comment = self.blank_lines
                    self.blank_lines = 0
                    if COMMENT_WITH_NL:
                        # The comment also ends a physical line
                        self.tokens = []
        return self.report.get_file_results()


class BaseReport(object):
    """Collect the results of the checks."""
    print_filename = False

    def __init__(self, options):
        self._benchmark_keys = options.benchmark_keys
        self._ignore_code = options.ignore_code
        # Results
        self.elapsed = 0
        self.total_errors = 0
        self.counters = dict.fromkeys(self._benchmark_keys, 0)
        self.messages = {}

    def start(self):
        """Start the timer."""
        self._start_time = time.time()

    def stop(self):
        """Stop the timer."""
        self.elapsed = time.time() - self._start_time

    def init_file(self, filename, lines, expected, line_offset):
        """Signal a new file."""
        self.filename = filename
        self.lines = lines
        self.expected = expected or ()
        self.line_offset = line_offset
        self.file_errors = 0
        self.counters['files'] += 1
        self.counters['physical lines'] += len(lines)

    def increment_logical_line(self):
        """Signal a new logical line."""
        self.counters['logical lines'] += 1

    def error(self, line_number, offset, text, check):
        """Report an error, according to options."""
        code = text[:4]
        if self._ignore_code(code):
            return
        if code in self.counters:
            self.counters[code] += 1
        else:
            self.counters[code] = 1
            self.messages[code] = text[5:]
        # Don't care about expected errors or warnings
        if code in self.expected:
            return
        if self.print_filename and not self.file_errors:
            print(self.filename)
        self.file_errors += 1
        self.total_errors += 1
        return code

    def get_file_results(self):
        """Return the count of errors and warnings for this file."""
        return self.file_errors

    def get_count(self, prefix=''):
        """Return the total count of errors and warnings."""
        return sum([self.counters[key]
                    for key in self.messages if key.startswith(prefix)])

    def get_statistics(self, prefix=''):
        """
        Get statistics for message codes that start with the prefix.

        prefix='' matches all errors and warnings
        prefix='E' matches all errors
        prefix='W' matches all warnings
        prefix='E4' matches all errors that have to do with imports
        """
        return ['%-7s %s %s' % (self.counters[key], key, self.messages[key])
                for key in sorted(self.messages) if key.startswith(prefix)]

    def print_statistics(self, prefix=''):
        """Print overall statistics (number of errors and warnings)."""
        for line in self.get_statistics(prefix):
            print(line)

    def print_benchmark(self):
        """Print benchmark numbers."""
        print('%-7.2f %s' % (self.elapsed, 'seconds elapsed'))
        if self.elapsed:
            for key in self._benchmark_keys:
                print('%-7d %s per second (%d total)' %
                      (self.counters[key] / self.elapsed, key,
                       self.counters[key]))


class FileReport(BaseReport):
    """Collect the results of the checks and print only the filenames."""
    print_filename = True


class StandardReport(BaseReport):
    """Collect and print the results of the checks."""

    def __init__(self, options):
        super(StandardReport, self).__init__(options)
        self._fmt = REPORT_FORMAT.get(options.format.lower(),
                                      options.format)
        self._repeat = options.repeat
        self._show_source = options.show_source
        self._show_pep8 = options.show_pep8

    def init_file(self, filename, lines, expected, line_offset):
        """Signal a new file."""
        self._deferred_print = []
        return super(StandardReport, self).init_file(
            filename, lines, expected, line_offset)

    def error(self, line_number, offset, text, check):
        """Report an error, according to options."""
        code = super(StandardReport, self).error(line_number, offset,
                                                 text, check)
        if code and (self.counters[code] == 1 or self._repeat):
            self._deferred_print.append(
                (line_number, offset, code, text[5:], check.__doc__))
        return code

    def get_file_results(self):
        """Print the result and return the overall count for this file."""
        self._deferred_print.sort()
        for line_number, offset, code, text, doc in self._deferred_print:
            print(self._fmt % {
                'path': self.filename,
                'row': self.line_offset + line_number, 'col': offset + 1,
                'code': code, 'text': text,
            })
            if self._show_source:
                if line_number > len(self.lines):
                    line = ''
                else:
                    line = self.lines[line_number - 1]
                print(line.rstrip())
                print(' ' * offset + '^')
            if self._show_pep8 and doc:
                print(doc.lstrip('\n').rstrip())
        return self.file_errors


class DiffReport(StandardReport):
    """Collect and print the results for the changed lines only."""

    def __init__(self, options):
        super(DiffReport, self).__init__(options)
        self._selected = options.selected_lines

    def error(self, line_number, offset, text, check):
        if line_number not in self._selected[self.filename]:
            return
        return super(DiffReport, self).error(line_number, offset, text, check)


class StyleGuide(object):
    """Initialize a PEP-8 instance with few options."""

    def __init__(self, *args, **kwargs):
        # build options from the command line
        self.checker_class = kwargs.pop('checker_class', Checker)
        parse_argv = kwargs.pop('parse_argv', False)
        config_file = kwargs.pop('config_file', None)
        parser = kwargs.pop('parser', None)
        options, self.paths = process_options(
            parse_argv=parse_argv, config_file=config_file, parser=parser)
        if args or kwargs:
            # build options from dict
            options_dict = dict(*args, **kwargs)
            options.__dict__.update(options_dict)
            if 'paths' in options_dict:
                self.paths = options_dict['paths']

        self.runner = self.input_file
        self.options = options

        if not options.reporter:
            options.reporter = BaseReport if options.quiet else StandardReport

        for index, value in enumerate(options.exclude):
            options.exclude[index] = value.rstrip('/')
        options.select = tuple(options.select or ())
        if not (options.select or options.ignore or
                options.testsuite or options.doctest) and DEFAULT_IGNORE:
            # The default choice: ignore controversial checks
            options.ignore = tuple(DEFAULT_IGNORE.split(','))
        else:
            # Ignore all checks which are not explicitly selected
            options.ignore = ('',) if options.select else tuple(options.ignore)
        options.benchmark_keys = BENCHMARK_KEYS[:]
        options.ignore_code = self.ignore_code
        options.physical_checks = self.get_checks('physical_line')
        options.logical_checks = self.get_checks('logical_line')
        options.ast_checks = self.get_checks('tree')
        self.init_report()

    def init_report(self, reporter=None):
        """Initialize the report instance."""
        self.options.report = (reporter or self.options.reporter)(self.options)
        return self.options.report

    def check_files(self, paths=None):
        """Run all checks on the paths."""
        if paths is None:
            paths = self.paths
        report = self.options.report
        runner = self.runner
        report.start()
        try:
            for path in paths:
                if os.path.isdir(path):
                    self.input_dir(path)
                elif not self.excluded(path):
                    runner(path)
        except KeyboardInterrupt:
            print('... stopped')
        report.stop()
        return report

    def input_file(self, filename, lines=None, expected=None, line_offset=0):
        """Run all checks on a Python source file."""
        if self.options.verbose:
            print('checking %s' % filename)
        fchecker = self.checker_class(
            filename, lines=lines, options=self.options)
        return fchecker.check_all(expected=expected, line_offset=line_offset)

    def input_dir(self, dirname):
        """Check all files in this directory and all subdirectories."""
        dirname = dirname.rstrip('/')
        if self.excluded(dirname):
            return 0
        counters = self.options.report.counters
        verbose = self.options.verbose
        filepatterns = self.options.filename
        runner = self.runner
        for root, dirs, files in os.walk(dirname):
            if verbose:
                print('directory ' + root)
            counters['directories'] += 1
            for subdir in sorted(dirs):
                if self.excluded(subdir, root):
                    dirs.remove(subdir)
            for filename in sorted(files):
                # contain a pattern that matches?
                if ((filename_match(filename, filepatterns) and
                     not self.excluded(filename, root))):
                    runner(os.path.join(root, filename))

    def excluded(self, filename, parent=None):
        """
        Check if options.exclude contains a pattern that matches filename.
        """
        if not self.options.exclude:
            return False
        basename = os.path.basename(filename)
        if filename_match(basename, self.options.exclude):
            return True
        if parent:
            filename = os.path.join(parent, filename)
        return filename_match(filename, self.options.exclude)

    def ignore_code(self, code):
        """
        Check if the error code should be ignored.

        If 'options.select' contains a prefix of the error code,
        return False.  Else, if 'options.ignore' contains a prefix of
        the error code, return True.
        """
        return (code.startswith(self.options.ignore) and
                not code.startswith(self.options.select))

    def get_checks(self, argument_name):
        """
        Find all globally visible functions where the first argument name
        starts with argument_name and which contain selected tests.
        """
        checks = []
        for check, attrs in _checks[argument_name].items():
            (codes, args) = attrs
            if any(not (code and self.ignore_code(code)) for code in codes):
                checks.append((check.__name__, check, args))
        return sorted(checks)


def get_parser(prog='pep8', version=__version__):
    parser = OptionParser(prog=prog, version=version,
                          usage="%prog [options] input ...")
    parser.config_options = [
        'exclude', 'filename', 'select', 'ignore', 'max-line-length', 'count',
        'format', 'quiet', 'show-pep8', 'show-source', 'statistics', 'verbose']
    parser.add_option('-v', '--verbose', default=0, action='count',
                      help="print status messages, or debug with -vv")
    parser.add_option('-q', '--quiet', default=0, action='count',
                      help="report only file names, or nothing with -qq")
    parser.add_option('-r', '--repeat', default=True, action='store_true',
                      help="(obsolete) show all occurrences of the same error")
    parser.add_option('--first', action='store_false', dest='repeat',
                      help="show first occurrence of each error")
    parser.add_option('--exclude', metavar='patterns', default=DEFAULT_EXCLUDE,
                      help="exclude files or directories which match these "
                           "comma separated patterns (default: %default)")
    parser.add_option('--filename', metavar='patterns', default='*.py',
                      help="when parsing directories, only check filenames "
                           "matching these comma separated patterns "
                           "(default: %default)")
    parser.add_option('--select', metavar='errors', default='',
                      help="select errors and warnings (e.g. E,W6)")
    parser.add_option('--ignore', metavar='errors', default='',
                      help="skip errors and warnings (e.g. E4,W)")
    parser.add_option('--show-source', action='store_true',
                      help="show source code for each error")
    parser.add_option('--show-pep8', action='store_true',
                      help="show text of PEP 8 for each error "
                           "(implies --first)")
    parser.add_option('--statistics', action='store_true',
                      help="count errors and warnings")
    parser.add_option('--count', action='store_true',
                      help="print total number of errors and warnings "
                           "to standard error and set exit code to 1 if "
                           "total is not null")
    parser.add_option('--max-line-length', type='int', metavar='n',
                      default=MAX_LINE_LENGTH,
                      help="set maximum allowed line length "
                           "(default: %default)")
    parser.add_option('--format', metavar='format', default='default',
                      help="set the error format [default|pylint|<custom>]")
    parser.add_option('--diff', action='store_true',
                      help="report only lines changed according to the "
                           "unified diff received on STDIN")
    group = parser.add_option_group("Testing Options")
    if os.path.exists(TESTSUITE_PATH):
        group.add_option('--testsuite', metavar='dir',
                         help="run regression tests from dir")
        group.add_option('--doctest', action='store_true',
                         help="run doctest on myself")
    group.add_option('--benchmark', action='store_true',
                     help="measure processing speed")
    return parser


def read_config(options, args, arglist, parser):
    """Read both user configuration and local configuration."""
    config = RawConfigParser()

    user_conf = options.config
    if user_conf and os.path.isfile(user_conf):
        if options.verbose:
            print('user configuration: %s' % user_conf)
        config.read(user_conf)

    parent = tail = args and os.path.abspath(os.path.commonprefix(args))
    while tail:
        if config.read([os.path.join(parent, fn) for fn in PROJECT_CONFIG]):
            if options.verbose:
                print('local configuration: in %s' % parent)
            break
        parent, tail = os.path.split(parent)

    pep8_section = parser.prog
    if config.has_section(pep8_section):
        option_list = dict([(o.dest, o.type or o.action)
                            for o in parser.option_list])

        # First, read the default values
        new_options, _ = parser.parse_args([])

        # Second, parse the configuration
        for opt in config.options(pep8_section):
            if options.verbose > 1:
                print("  %s = %s" % (opt, config.get(pep8_section, opt)))
            if opt.replace('_', '-') not in parser.config_options:
                print("Unknown option: '%s'\n  not in [%s]" %
                      (opt, ' '.join(parser.config_options)))
                sys.exit(1)
            normalized_opt = opt.replace('-', '_')
            opt_type = option_list[normalized_opt]
            if opt_type in ('int', 'count'):
                value = config.getint(pep8_section, opt)
            elif opt_type == 'string':
                value = config.get(pep8_section, opt)
            else:
                assert opt_type in ('store_true', 'store_false')
                value = config.getboolean(pep8_section, opt)
            setattr(new_options, normalized_opt, value)

        # Third, overwrite with the command-line options
        options, _ = parser.parse_args(arglist, values=new_options)
    options.doctest = options.testsuite = False
    return options


def process_options(arglist=None, parse_argv=False, config_file=None,
                    parser=None):
    """Process options passed either via arglist or via command line args."""
    if not arglist and not parse_argv:
        # Don't read the command line if the module is used as a library.
        arglist = []
    if not parser:
        parser = get_parser()
    if not parser.has_option('--config'):
        if config_file is True:
            config_file = DEFAULT_CONFIG
        group = parser.add_option_group("Configuration", description=(
            "The project options are read from the [%s] section of the "
            "tox.ini file or the setup.cfg file located in any parent folder "
            "of the path(s) being processed.  Allowed options are: %s." %
            (parser.prog, ', '.join(parser.config_options))))
        group.add_option('--config', metavar='path', default=config_file,
                         help="user config file location (default: %default)")
    options, args = parser.parse_args(arglist)
    options.reporter = None

    if options.ensure_value('testsuite', False):
        args.append(options.testsuite)
    elif not options.ensure_value('doctest', False):
        if parse_argv and not args:
            if options.diff or any(os.path.exists(name)
                                   for name in PROJECT_CONFIG):
                args = ['.']
            else:
                parser.error('input not specified')
        options = read_config(options, args, arglist, parser)
        options.reporter = parse_argv and options.quiet == 1 and FileReport

    options.filename = options.filename and options.filename.split(',')
    options.exclude = options.exclude.split(',')
    options.select = options.select and options.select.split(',')
    options.ignore = options.ignore and options.ignore.split(',')

    if options.diff:
        options.reporter = DiffReport
        stdin = stdin_get_value()
        options.selected_lines = parse_udiff(stdin, options.filename, args[0])
        args = sorted(options.selected_lines)

    return options, args


def _main():
    """Parse options and run checks on Python source."""
    pep8style = StyleGuide(parse_argv=True, config_file=True)
    options = pep8style.options
    if options.doctest or options.testsuite:
        from testsuite.support import run_tests
        report = run_tests(pep8style)
    else:
        report = pep8style.check_files()
    if options.statistics:
        report.print_statistics()
    if options.benchmark:
        report.print_benchmark()
    if options.testsuite and not options.quiet:
        report.print_results()
    if report.total_errors:
        if options.count:
            sys.stderr.write(str(report.total_errors) + '\n')
        sys.exit(1)

if __name__ == '__main__':
    _main()
