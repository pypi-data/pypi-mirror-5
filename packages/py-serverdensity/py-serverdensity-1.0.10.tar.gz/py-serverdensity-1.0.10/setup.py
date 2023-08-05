"""Installer for py-serverdensity
"""

import os
cwd = os.path.dirname(__file__)
__version__ = open(os.path.join(cwd, 'serverdensity', 'api', 'version.txt'), 'r').read().strip()

try:
        from setuptools import setup, find_packages
except ImportError:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup, find_packages
setup(
    name='py-serverdensity',
    description='Python ServerDensity.com API wrapper',
    long_description=open('README.rst').read(),
    version=__version__,
    author='Wes Mason',
    author_email='wes@serverdensity.com',
    url='https://github.com/serverdensity/py-serverdensity',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=open('requirements.txt').readlines(),
    package_data={'serverdensity/api': ['version.txt']},
    include_package_data=True,
    license='BSD'
)
