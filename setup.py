import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='rodong',
    version='1.0.0',
    description='Scrape articles from Rodong Sinumn, the North Korean news agency',
    long_description=read('README.rst'),
    url='https://github.com/tdeck/rodong',
    license='MIT',
    author='Troy Deck',
    py_modules=['rodong'],
    install_requires=[
        'lxml==3.4.2',
        'requests==2.5.1'
    ],
    include_package_data=True
)
