#!/usr/bin/env python
import codecs
import os.path
import re
from setuptools import setup, find_packages

def pkg_path(*components):
    path = os.path.join(os.path.dirname(__file__), *components)
    return os.path.realpath(path)

def get_readme():
    with codecs.open(pkg_path('README.rst'), encoding='utf-8') as readme:
        return readme.read()

def get_version():
    init_path = pkg_path('discoverage', '__init__.py')
    with codecs.open(init_path, encoding='utf-8') as init:
        contents = init.read()
        match = re.search(r'__version__ = [\'"]([.\w]+)[\'"]', contents)
        return match.group(1)

setup(
    name='django-discoverage',
    version=get_version(),
    author='Ryan Kaskel',
    author_email='dev@ryankaskel.com',
    url='https://github.com/ryankask/django-discoverage',
    packages=find_packages(),
    install_requires=['coverage>=3.6', 'django-discover-runner>=0.4'],
    description='Jannis Leidel and Carl Meyer\'s django-discover-runner with coverage.',
    long_description=get_readme(),
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Testing',
    ]
)
