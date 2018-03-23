"""Packaging settings."""


from codecs import open
from os.path import abspath
from os.path import dirname
from os.path import join
from subprocess import call

from setuptools import Command
from setuptools import setup

from aimbrain import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=aimbrain', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name='aimbrain-cli',
    version=__version__,
    description='A CLI to run common aimbrain tasks.',
    long_description=long_description,
    url='https://github.com/aimbrain/aimbrain-cli',
    author='Sam Lacey',
    author_email='sam@aimbrain.com',
    license='MIT',
    keywords='cli',
    packages=['aimbrain', 'aimbrain.commands', 'aimbrain.commands.utils'],
    install_requires=[
        'docopt==0.6.2',
        'opencv-python==3.4.0.12',
        'requests==2.18.4',
        'numpy==1.14.0',
        'pillow==5.0.0',
        'scipy==1.0.0',
        'unittest2==1.1.0',
        'pytest==3.4.2',
        'mock==2.0.0',
    ],
    extras_require={'test': ['coverage', 'pytest', 'pytest-cov']},
    entry_points='''
        [console_scripts]
        aimbrain-cli=aimbrain.aimbrain:main
    ''',
    cmdclass={'test': RunTests},
)
