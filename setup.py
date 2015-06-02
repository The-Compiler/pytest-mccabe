from setuptools import setup

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
    install_requires=['pytest-cache', 'pytest>=2.3.dev14', 'mccabe'])
