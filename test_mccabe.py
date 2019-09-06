# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

pytest_plugins = "pytester",  # pylint: disable=invalid-name


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
    result = testdir.runpytest("--mccabe")
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


def test_config(testdir):
    testdir.makeini("""
[pytest]
mccabe-complexity=
    foo*.py 1
    * 10
""")

    testdir.makepyfile(foobar="""
def f():
    for i in range(10):
        print(i)
""",
                       fish="""
def g():
    for i in range(10):
        print(i)
""")
    result = testdir.runpytest("--mccabe")
    assert "'f' is too complex" in result.stdout.str()  # FIXME
    assert "'g' is too complex" not in result.stdout.str()  # FIXME
    assert '1 failed, 1 passed' in result.stdout.str()


def test_pep263(testdir):
    testdir.makepyfile(b'\n# encoding=utf-8\n\nsnowman = '
                       b'"\xe2\x98\x83"\n'.decode("utf-8"))
    result = testdir.runpytest("--mccabe")
    assert '1 passed' in result.stdout.str()


def test_strict(testdir):
    testdir.makepyfile(test_foo="""
def test_foo():
    pass
""")
    result = testdir.runpytest("--strict")
    assert result.ret == 0
