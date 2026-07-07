import fnmatch
# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

import sys
from pathlib import Path
import tokenize

import py
import pytest
import mccabe
import _ast


HISTKEY = "mccabe/mtimes"


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption(
        '--mccabe', action='store_true',
        help="run mccabe on .py files")
    parser.addini(
        "mccabe-complexity", type="linelist",
        help="each line specifies a glob pattern and whitespace "
             "separated the maximal complexity for the given pattern (or 0 to "
             "deactivate checking). example: *.py 10")


def pytest_configure(config):
    config.addinivalue_line('markers', 'mccabe: Tests that run mccabe')


def pytest_sessionstart(session):
    config = session.config
    if config.option.mccabe:
        config._mccabe_complexities = Complexities(
            config.getini("mccabe-complexity"))
        config._mccabe_mtimes = config.cache.get(HISTKEY, {})


def pytest_collect_file(file_path, parent):
    config = parent.config
    if config.option.mccabe and file_path.suffix == '.py':
        complexity = config._mccabe_complexities(file_path)
        if complexity != 0:
            return McCabeFile.from_parent(parent=parent,
                                          path=file_path,
                                          complexity=complexity)
    return None

def pytest_sessionfinish(session):
    config = session.config
    if hasattr(config, "_mccabe_mtimes"):
        config.cache.set(HISTKEY, config._mccabe_mtimes)


class McCabeError(Exception):
    """ indicates an error during McCabe checks. """


class McCabeFile(pytest.File):

    def __init__(self, path, parent, complexity):
        super().__init__(path=path, parent=parent)
        self.complexity = complexity

    def collect(self):
        yield McCabeItem.from_parent(parent=self,
                                     name=str(self.path),
                                     path=self.path,
                                     complexity=self.complexity)


class McCabeItem(pytest.Item):

    def __init__(self, name, parent, path, complexity):
        super().__init__(name=name, parent=parent)
        self.path = path
        self._mtime = None
        if hasattr(self, 'add_marker'):
            self.add_marker("mccabe")
        else:
            self.keywords["mccabe"] = True
        self.complexity = complexity

    def setup(self):
        mtimes = self.config._mccabe_mtimes
        self._mtime = self.path.stat().st_mtime
        old = mtimes.get(str(self.path), 0)
        if old == (self._mtime, self.complexity):
            pytest.skip("file(s) previously passed McCabe checks")

    def runtest(self):
        found_errors, out = check_file(str(self.path), self.complexity)
        if found_errors:
            raise McCabeError("\n".join(out))
        # update mtime only if test passed
        # otherwise failures would not be re-run next time
        self.config._mccabe_mtimes[str(self.path)] = (self._mtime,
                                                       self.complexity)

    def repr_failure(self, excinfo, style=None):
        if excinfo.errisinstance(McCabeError):
            return str(excinfo.value)
        return super().repr_failure(excinfo, style)

    def reportinfo(self):
        return self.path, -1, "mccabe-check"


class Complexities:

    DEFAULT_COMPLEXITY = 7

    def __init__(self, lines):
        self.complexities = []
        for line in lines:
            i = line.find("#")
            if i != -1:
                line = line[:i]
            try:
                glob, val = line.split(None, 1)
            except ValueError:
                glob, val = None, line
            self.complexities.append((glob, int(val)))

    def __call__(self, path):
        for (glob, complexity) in self.complexities:
            path_text = str(path)
            path_name = Path(path).name
            if not glob or fnmatch.fnmatch(path_name, glob) or fnmatch.fnmatch(path_text, glob):
                return complexity
        return self.DEFAULT_COMPLEXITY


def check_file(path, complexity):
    path = Path(path)
    if not hasattr(tokenize, 'open'):
        code = path.read_text()
    else:
        with tokenize.open(str(path)) as f:
            code = f.read()

    filename = str(path)
    try:
        tree = compile(code, filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError as exc:
        lineno = exc.lineno or 1
        return 1, ["%s:%s: invalid syntax" % (filename, lineno)]

    errors = []
    checker = mccabe.McCabeChecker(tree, filename)
    checker.max_complexity = complexity
    lines = code.split('\n')
    for lineno, _offset, text, _checker in checker.run():
        if is_ignored_line(lines[lineno - 1].strip()):
            continue
        errors.append('%s:%s: %s' % (filename, lineno, text))
    return len(errors), errors


def get_syntax_error_msg(filename):
    errors = []
    value = sys.exc_info()[1]
    (lineno, offset, text) = value.lineno, value.offset, value.text
    if text is None:
        errors.append("%s: problem decoding source" % filename)
    else:
        line = text.splitlines()[-1]

        if offset is not None:
            offset = offset - (len(text) - len(line))

        msg = '%s:%d: %s' % (filename, lineno, value.args[0])
        msg = "%s\n%s" % (msg, line)

        if offset is not None:
            msg = "%s\n%s" % (msg, "%s^" % (" " * offset))
        errors.append(msg)
    return errors


def is_ignored_line(line):
    return line.endswith('# noqa') or line.endswith('# pragma: no mccabe')
