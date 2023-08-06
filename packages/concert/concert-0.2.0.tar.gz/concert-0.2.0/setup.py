import os
from concert import __version__
from setuptools import setup, find_packages


# Install Bash completion script only if installation is run as root
if os.geteuid() != 0:
    data_files = []
else:
    data_files = [('/etc/bash_completion.d', ['extras/completion/concert.sh'])]


setup(
    name='concert',
    version=__version__,
    author='Matthias Vogelgesang',
    author_email='matthias.vogelgesang@kit.edu',
    url='http://github.com/ufo-kit/concert',
    license='LGPL',
    packages=find_packages(exclude=['*.tests']),
    scripts=['bin/concert'],
    data_files=data_files,
    exclude_package_data={'': ['README.rst']},
    description="Lightweight beamline control system",
    long_description=open('README.rst').read(),
    install_requires=['argparse >= 1.2.1',
                      'futures >= 2.1.3',
                      'logbook >= 0.4.0',
                      'numpy >= 1.3.0',
                      'prettytable >= 0.7.2',
                      'pyxdg >= 0.20',
                      'quantities >= 0.10.1',
                      'scipy >= 0.7.2'],
    tests_require=['nose>=1.2.1',
                   'testfixtures>=3.0.0'],
    test_suite='concert.tests',
)
