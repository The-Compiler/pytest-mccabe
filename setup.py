import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """
    Overrides setup "test" command, taken from here:
    http://pytest.org/latest/goodpractises.html
    """

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main([])
        sys.exit(errno)


setup(
    name='pytest-mccabe',
    description='pytest plugin to run the mccabe code complexity checker.',
    long_description=open("README.rst").read(),
    license="MIT license",
    version='0.1',
    author='Florian Bruhin',
    author_email='me@the-compiler.org',
    url='https://github.com/The-Compiler/pytest-mccabe',
    py_modules=['pytest_mccabe'],
    entry_points={'pytest11': ['mccabe = pytest_mccabe']},
    install_requires=['pytest-cache', 'pytest>=2.3.dev14', 'mccabe'],
    zip_safe=True,
    classifiers=[
        'Environment :: Plugins',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
    keywords='pytest plugin mccabe complexity',
    tests_requires=['pytest'],
    cmdclass={'test': PyTest},
)
