# coding=utf8
pytest_plugins = "pytester",


def test_too_complex(testdir):
    testdir.makeini("""
[pytest]
mccabe-complexity=1
""")
    testdir.makepyfile("""
def f():
    for i in range(10):
        print(i)
""")
    result = testdir.runpytest("--mccabe")
    assert "is too complex" in result.stdout.str()
    assert 'passed' not in result.stdout.str()


def test_syntax_error(testdir):
    testdir.makeini("""
[pytest]
python_files=check_*.py
""")
    testdir.makepyfile("""
for x in []
    pass
""")
    result = testdir.runpytest("--mccabe", "--ignore", testdir)
    assert "1: invalid syntax" in result.stdout.str()
    assert 'passed' not in result.stdout.str()


def test_noqa(testdir):
    testdir.makeini("""
[pytest]
python_files=check_*.py
mccabe-complexity=1
""")
    testdir.makepyfile("""
def f():  # noqa
    for i in range(10):
        print(i)

def g():  # pragma: no mccabe
    for i in range(10):
        print(i)

def h():  # this will get checked
    for i in range(10):
        print(i)
""")
    result = testdir.runpytest("--mccabe")
    assert "'f' is too complex" not in result.stdout.str()  # FIXME
    assert "'g' is too complex" not in result.stdout.str()  # FIXME
    assert "'h' is too complex" in result.stdout.str()  # FIXME
    assert 'passed' not in result.stdout.str()


def test_pep263(testdir):
    testdir.makepyfile(b'\n# encoding=utf-8\n\nsnowman = "\xe2\x98\x83"\n'.decode("utf-8"))
    result = testdir.runpytest("--mccabe")
    assert '1 passed in' in result.stdout.str()
